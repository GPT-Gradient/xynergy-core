/**
 * Token Management Service
 * Handles token retrieval, refresh, and caching
 */

import axios from 'axios';
import { getFirestore } from 'firebase-admin/firestore';
import { logger } from '../utils/logger';
import { redisClient } from '../utils/redis';
import { kmsService } from '../utils/kms';
import { getProviderConfig } from '../utils/providers';
import {
  GetTokenRequest,
  GetTokenResponse,
  OAuthConnection,
  TokenRefreshResult,
} from '../types';

export class TokenService {
  private get db() {
    return getFirestore();
  }

  /**
   * Get access token for a user's OAuth connection
   * Returns cached token if available, otherwise decrypts from Firestore
   */
  async getToken(request: GetTokenRequest): Promise<GetTokenResponse> {
    try {
      // Find connection
      let query = this.db
        .collection('oauth_connections')
        .where('userId', '==', request.userId)
        .where('tenantId', '==', request.tenantId)
        .where('provider', '==', request.provider)
        .where('status', '==', 'active');

      // Add team filter for Slack multi-workspace
      if (request.teamId) {
        query = query.where('providerTeamId', '==', request.teamId);
      }

      const querySnapshot = await query.get();

      if (querySnapshot.empty) {
        throw new Error('No active OAuth connection found');
      }

      const connectionDoc = querySnapshot.docs[0];
      const connection = connectionDoc.data() as OAuthConnection;

      // Check if token expired
      const now = new Date();
      const expiresAt = new Date(connection.expiresAt);

      if (expiresAt <= now) {
        // Token expired - attempt refresh
        logger.info('Token expired, attempting refresh', {
          connectionId: connection.id,
          provider: connection.provider,
        });

        await this.refreshToken(connection.id);

        // Re-fetch connection after refresh
        const refreshedDoc = await this.db.collection('oauth_connections').doc(connection.id).get();
        const refreshedConnection = refreshedDoc.data() as OAuthConnection;

        return {
          accessToken: await this.getDecryptedToken(refreshedConnection),
          tokenType: refreshedConnection.tokenType,
          expiresAt: refreshedConnection.expiresAt,
          scopes: refreshedConnection.scopes,
        };
      }

      // Check cache first
      const cachedToken = await redisClient.getCachedToken(connection.id);

      if (cachedToken) {
        logger.debug('Token retrieved from cache', { connectionId: connection.id });
        return {
          accessToken: cachedToken,
          tokenType: connection.tokenType,
          expiresAt: connection.expiresAt,
          scopes: connection.scopes,
        };
      }

      // Decrypt token
      const accessToken = await this.getDecryptedToken(connection);

      // Cache for future requests
      await redisClient.cacheToken(connection.id, accessToken);

      return {
        accessToken,
        tokenType: connection.tokenType,
        expiresAt: connection.expiresAt,
        scopes: connection.scopes,
      };
    } catch (error) {
      logger.error('Error getting token', { error, request });
      throw error;
    }
  }

  /**
   * Refresh an OAuth token
   */
  async refreshToken(connectionId: string): Promise<TokenRefreshResult> {
    try {
      // Get connection
      const connectionDoc = await this.db.collection('oauth_connections').doc(connectionId).get();

      if (!connectionDoc.exists) {
        throw new Error('Connection not found');
      }

      const connection = connectionDoc.data() as OAuthConnection;

      // Check if refresh token available
      if (!connection.encryptedRefreshToken) {
        logger.warn('No refresh token available', { connectionId, provider: connection.provider });
        return {
          connectionId,
          provider: connection.provider,
          success: false,
          error: 'No refresh token available',
        };
      }

      // Decrypt refresh token
      const refreshToken = await kmsService.decryptToken(connection.encryptedRefreshToken);

      const config = getProviderConfig(connection.provider);

      // Refresh token with provider
      const params = new URLSearchParams({
        grant_type: 'refresh_token',
        refresh_token: refreshToken,
        client_id: config.clientId,
        client_secret: config.clientSecret,
      });

      const response = await axios.post(config.tokenUrl, params.toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      // Encrypt new access token
      const encryptedAccessToken = await kmsService.encryptToken(response.data.access_token);

      // Encrypt new refresh token if provided
      const encryptedRefreshToken = response.data.refresh_token
        ? await kmsService.encryptToken(response.data.refresh_token)
        : connection.encryptedRefreshToken;

      // Calculate new expiry
      const now = new Date();
      const expiresAt = new Date(now.getTime() + response.data.expires_in * 1000);

      // Update connection
      await this.db.collection('oauth_connections').doc(connectionId).update({
        encryptedAccessToken,
        encryptedRefreshToken,
        expiresAt: expiresAt.toISOString(),
        updatedAt: now.toISOString(),
        lastRefreshedAt: now.toISOString(),
        status: 'active',
      });

      // Invalidate cache
      await redisClient.invalidateToken(connectionId);

      // Cache new token
      await redisClient.cacheToken(connectionId, response.data.access_token);

      logger.info('Token refreshed successfully', {
        connectionId,
        provider: connection.provider,
        newExpiresAt: expiresAt.toISOString(),
      });

      return {
        connectionId,
        provider: connection.provider,
        success: true,
        newExpiresAt: expiresAt.toISOString(),
      };
    } catch (error: any) {
      logger.error('Token refresh failed', {
        error: error.response?.data || error.message,
        connectionId,
      });

      // Mark connection as error
      await this.db.collection('oauth_connections').doc(connectionId).update({
        status: 'error',
        updatedAt: new Date().toISOString(),
      });

      return {
        connectionId,
        provider: 'slack', // Default, will be overwritten
        success: false,
        error: error.message,
      };
    }
  }

  /**
   * Refresh all expiring tokens (called by background job)
   */
  async refreshExpiringTokens(): Promise<TokenRefreshResult[]> {
    try {
      // Find tokens expiring in the next hour
      const oneHourFromNow = new Date(Date.now() + 60 * 60 * 1000);

      const expiringQuery = await this.db
        .collection('oauth_connections')
        .where('status', '==', 'active')
        .where('expiresAt', '<=', oneHourFromNow.toISOString())
        .get();

      logger.info('Found expiring tokens', { count: expiringQuery.size });

      const results: TokenRefreshResult[] = [];

      for (const doc of expiringQuery.docs) {
        const result = await this.refreshToken(doc.id);
        results.push(result);
      }

      const successCount = results.filter(r => r.success).length;
      logger.info('Token refresh batch completed', {
        total: results.length,
        successful: successCount,
        failed: results.length - successCount,
      });

      return results;
    } catch (error) {
      logger.error('Error refreshing expiring tokens', { error });
      throw error;
    }
  }

  /**
   * Revoke an OAuth connection
   */
  async revokeConnection(connectionId: string, revokedBy: string, reason?: string): Promise<void> {
    try {
      const now = new Date().toISOString();

      await this.db.collection('oauth_connections').doc(connectionId).update({
        status: 'revoked',
        revokedAt: now,
        revokedBy,
        revokedReason: reason,
        updatedAt: now,
      });

      // Invalidate cache
      await redisClient.invalidateToken(connectionId);

      logger.info('Connection revoked', { connectionId, revokedBy, reason });
    } catch (error) {
      logger.error('Error revoking connection', { error, connectionId });
      throw error;
    }
  }

  /**
   * Helper: Decrypt access token from connection
   */
  private async getDecryptedToken(connection: OAuthConnection): Promise<string> {
    try {
      return await kmsService.decryptToken(connection.encryptedAccessToken);
    } catch (error) {
      logger.error('Error decrypting token', { error, connectionId: connection.id });
      throw new Error('Failed to decrypt access token');
    }
  }
}
