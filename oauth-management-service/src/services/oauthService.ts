/**
 * OAuth Service
 * Handles OAuth URL generation and callback processing
 */

import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import { getFirestore } from 'firebase-admin/firestore';
import { logger } from '../utils/logger';
import { redisClient } from '../utils/redis';
import { kmsService } from '../utils/kms';
import { getProviderConfig } from '../utils/providers';
import {
  GenerateOAuthUrlRequest,
  GenerateOAuthUrlResponse,
  OAuthCallbackRequest,
  OAuthCallbackResponse,
  OAuthState,
  OAuthConnection,
  TokenExchangeResponse,
} from '../types';

export class OAuthService {
  private get db() {
    return getFirestore();
  }

  /**
   * Generate OAuth authorization URL
   */
  async generateAuthUrl(request: GenerateOAuthUrlRequest): Promise<GenerateOAuthUrlResponse> {
    try {
      const config = getProviderConfig(request.provider);

      // Generate unique state parameter
      const state = uuidv4();
      const now = new Date();
      const expiresAt = new Date(now.getTime() + 15 * 60 * 1000); // 15 minutes

      // Store state in Redis
      const stateData: OAuthState = {
        userId: request.userId,
        tenantId: request.tenantId,
        provider: request.provider,
        redirectUri: request.redirectUri || config.redirectUri,
        createdAt: now.toISOString(),
        expiresAt: expiresAt.toISOString(),
      };

      await redisClient.storeState(state, stateData);

      // Build authorization URL
      const params = new URLSearchParams({
        client_id: config.clientId,
        redirect_uri: config.redirectUri,
        state: state,
        scope: config.scopes.join(' '),
        access_type: 'offline', // For refresh tokens (Gmail)
        prompt: 'consent', // Force consent to get refresh token (Gmail)
      });

      // Provider-specific parameters
      if (request.provider === 'slack') {
        params.append('user_scope', config.scopes.join(','));
      }

      const authorizationUrl = `${config.authorizationUrl}?${params.toString()}`;

      logger.info('OAuth URL generated', {
        provider: request.provider,
        userId: request.userId,
        tenantId: request.tenantId,
        state,
      });

      return {
        authorizationUrl,
        state,
        expiresAt: expiresAt.toISOString(),
      };
    } catch (error) {
      logger.error('Error generating OAuth URL', { error, request });
      throw error;
    }
  }

  /**
   * Handle OAuth callback and exchange code for tokens
   */
  async handleCallback(request: OAuthCallbackRequest): Promise<OAuthCallbackResponse> {
    try {
      // Retrieve and validate state
      const stateData = await redisClient.getState(request.state);

      if (!stateData) {
        throw new Error('Invalid or expired OAuth state');
      }

      // Check if state expired
      if (new Date(stateData.expiresAt) < new Date()) {
        throw new Error('OAuth state expired');
      }

      const config = getProviderConfig(stateData.provider);

      // Exchange code for tokens
      const tokenResponse = await this.exchangeCodeForTokens(
        stateData.provider,
        request.code,
        config.redirectUri
      );

      // Extract provider-specific user information
      const { providerUserId, providerTeamId, email } = this.extractUserInfo(
        stateData.provider,
        tokenResponse
      );

      // Encrypt tokens
      const encryptedAccessToken = await kmsService.encryptToken(tokenResponse.access_token);
      const encryptedRefreshToken = tokenResponse.refresh_token
        ? await kmsService.encryptToken(tokenResponse.refresh_token)
        : undefined;

      // Calculate token expiry
      const now = new Date();
      const expiresAt = new Date(now.getTime() + tokenResponse.expires_in * 1000);

      // Check if connection already exists
      const existingQuery = await this.db
        .collection('oauth_connections')
        .where('userId', '==', stateData.userId)
        .where('tenantId', '==', stateData.tenantId)
        .where('provider', '==', stateData.provider)
        .where('providerUserId', '==', providerUserId)
        .get();

      let connectionId: string;

      if (!existingQuery.empty) {
        // Update existing connection
        connectionId = existingQuery.docs[0].id;
        await this.db.collection('oauth_connections').doc(connectionId).update({
          encryptedAccessToken,
          encryptedRefreshToken,
          tokenType: tokenResponse.token_type,
          expiresAt: expiresAt.toISOString(),
          scopes: tokenResponse.scope ? tokenResponse.scope.split(' ') : config.scopes,
          status: 'active',
          updatedAt: now.toISOString(),
          lastRefreshedAt: now.toISOString(),
        });

        logger.info('OAuth connection updated', {
          connectionId,
          provider: stateData.provider,
          userId: stateData.userId,
        });
      } else {
        // Create new connection
        connectionId = uuidv4();
        const connection: OAuthConnection = {
          id: connectionId,
          userId: stateData.userId,
          tenantId: stateData.tenantId,
          provider: stateData.provider,
          providerUserId,
          providerTeamId,
          email,
          encryptedAccessToken,
          encryptedRefreshToken,
          tokenType: tokenResponse.token_type,
          expiresAt: expiresAt.toISOString(),
          scopes: tokenResponse.scope ? tokenResponse.scope.split(' ') : config.scopes,
          status: 'active',
          createdAt: now.toISOString(),
          updatedAt: now.toISOString(),
        };

        await this.db.collection('oauth_connections').doc(connectionId).set(connection);

        logger.info('OAuth connection created', {
          connectionId,
          provider: stateData.provider,
          userId: stateData.userId,
        });
      }

      // Cache decrypted token in Redis
      await redisClient.cacheToken(connectionId, tokenResponse.access_token);

      return {
        success: true,
        connectionId,
        provider: stateData.provider,
        email,
      };
    } catch (error) {
      logger.error('Error handling OAuth callback', { error, request });
      throw error;
    }
  }

  /**
   * Exchange authorization code for tokens
   */
  private async exchangeCodeForTokens(
    provider: 'slack' | 'gmail',
    code: string,
    redirectUri: string
  ): Promise<TokenExchangeResponse> {
    const config = getProviderConfig(provider);

    try {
      const params = new URLSearchParams({
        code,
        client_id: config.clientId,
        client_secret: config.clientSecret,
        redirect_uri: redirectUri,
      });

      if (provider === 'gmail') {
        params.append('grant_type', 'authorization_code');
      }

      const response = await axios.post<TokenExchangeResponse>(
        config.tokenUrl,
        params.toString(),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      logger.info('Token exchange successful', {
        provider,
        hasRefreshToken: !!response.data.refresh_token,
      });

      return response.data;
    } catch (error: any) {
      logger.error('Token exchange failed', {
        error: error.response?.data || error.message,
        provider,
      });
      throw new Error('Failed to exchange authorization code for tokens');
    }
  }

  /**
   * Extract user information from token response
   */
  private extractUserInfo(
    provider: 'slack' | 'gmail',
    tokenResponse: TokenExchangeResponse
  ): {
    providerUserId: string;
    providerTeamId?: string;
    email: string;
  } {
    if (provider === 'slack') {
      if (!tokenResponse.authed_user?.id) {
        throw new Error('Missing Slack user ID in token response');
      }

      return {
        providerUserId: tokenResponse.authed_user.id,
        providerTeamId: tokenResponse.team?.id,
        email: tokenResponse.authed_user.email || '',
      };
    } else if (provider === 'gmail') {
      // For Gmail, we need to make a separate API call to get user info
      // For now, return placeholder - will be filled by getUserInfo method
      return {
        providerUserId: '', // Will be set by getUserInfo
        email: '', // Will be set by getUserInfo
      };
    }

    throw new Error(`Unsupported provider: ${provider}`);
  }

  /**
   * Get Gmail user information from Google API
   */
  async getGmailUserInfo(accessToken: string): Promise<{ email: string; id: string }> {
    try {
      const response = await axios.get('https://www.googleapis.com/oauth2/v2/userinfo', {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      return {
        email: response.data.email,
        id: response.data.id,
      };
    } catch (error: any) {
      logger.error('Failed to get Gmail user info', { error: error.response?.data });
      throw new Error('Failed to get Gmail user information');
    }
  }
}
