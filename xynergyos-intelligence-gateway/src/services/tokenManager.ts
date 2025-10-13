import { Firestore } from '@google-cloud/firestore';
import { logger } from '../utils/logger';
import * as crypto from 'crypto';

/**
 * Token Manager - Manages OAuth tokens for users
 *
 * Features:
 * - Store encrypted OAuth tokens per user
 * - Automatic token refresh
 * - Token expiry tracking
 * - Multi-service support (Slack, Gmail, Calendar)
 */

interface OAuthToken {
  userId: string;
  tenantId: string;
  service: 'slack' | 'gmail' | 'calendar';
  accessToken: string;
  refreshToken?: string;
  expiresAt?: Date;
  scopes: string[];
  metadata: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

export class TokenManager {
  private firestore: Firestore;
  private encryptionKey: string;
  private readonly COLLECTION = 'oauth_tokens';

  constructor() {
    this.firestore = new Firestore();
    // In production, load from Secret Manager
    this.encryptionKey = process.env.TOKEN_ENCRYPTION_KEY || this.generateEncryptionKey();
  }

  /**
   * Store OAuth token for a user
   */
  async storeToken(
    userId: string,
    tenantId: string,
    service: 'slack' | 'gmail' | 'calendar',
    accessToken: string,
    options: {
      refreshToken?: string;
      expiresIn?: number; // seconds
      scopes?: string[];
      metadata?: Record<string, any>;
    } = {}
  ): Promise<void> {
    try {
      const encryptedAccessToken = this.encrypt(accessToken);
      const encryptedRefreshToken = options.refreshToken
        ? this.encrypt(options.refreshToken)
        : undefined;

      const expiresAt = options.expiresIn
        ? new Date(Date.now() + options.expiresIn * 1000)
        : undefined;

      const tokenData: OAuthToken = {
        userId,
        tenantId,
        service,
        accessToken: encryptedAccessToken,
        refreshToken: encryptedRefreshToken,
        expiresAt,
        scopes: options.scopes || [],
        metadata: options.metadata || {},
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const docId = `${userId}_${service}`;
      await this.firestore.collection(this.COLLECTION).doc(docId).set(tokenData);

      logger.info('OAuth token stored', {
        userId,
        service,
        tenantId,
        expiresAt: expiresAt?.toISOString(),
      });
    } catch (error) {
      logger.error('Failed to store OAuth token', { error, userId, service });
      throw error;
    }
  }

  /**
   * Get OAuth token for a user
   */
  async getToken(
    userId: string,
    service: 'slack' | 'gmail' | 'calendar'
  ): Promise<OAuthToken | null> {
    try {
      const docId = `${userId}_${service}`;
      const doc = await this.firestore.collection(this.COLLECTION).doc(docId).get();

      if (!doc.exists) {
        return null;
      }

      const data = doc.data() as OAuthToken;

      // Decrypt tokens
      data.accessToken = this.decrypt(data.accessToken);
      if (data.refreshToken) {
        data.refreshToken = this.decrypt(data.refreshToken);
      }

      // Check if token is expired
      if (data.expiresAt && new Date() >= data.expiresAt) {
        logger.info('Token expired, attempting refresh', { userId, service });
        return await this.refreshTokenIfNeeded(userId, service, data);
      }

      return data;
    } catch (error) {
      logger.error('Failed to get OAuth token', { error, userId, service });
      throw error;
    }
  }

  /**
   * Refresh token if expired
   */
  private async refreshTokenIfNeeded(
    userId: string,
    service: 'slack' | 'gmail' | 'calendar',
    tokenData: OAuthToken
  ): Promise<OAuthToken | null> {
    if (!tokenData.refreshToken) {
      logger.warn('No refresh token available', { userId, service });
      return null;
    }

    try {
      // Service-specific token refresh
      const newTokens = await this.refreshServiceToken(service, tokenData.refreshToken);

      if (newTokens) {
        // Update stored token
        await this.storeToken(userId, tokenData.tenantId, service, newTokens.accessToken, {
          refreshToken: newTokens.refreshToken || tokenData.refreshToken,
          expiresIn: newTokens.expiresIn,
          scopes: tokenData.scopes,
          metadata: tokenData.metadata,
        });

        // Return updated token data
        return await this.getToken(userId, service);
      }

      return null;
    } catch (error) {
      logger.error('Token refresh failed', { error, userId, service });
      return null;
    }
  }

  /**
   * Refresh service-specific token
   */
  private async refreshServiceToken(
    service: 'slack' | 'gmail' | 'calendar',
    refreshToken: string
  ): Promise<{ accessToken: string; refreshToken?: string; expiresIn: number } | null> {
    switch (service) {
      case 'slack':
        return await this.refreshSlackToken(refreshToken);
      case 'gmail':
      case 'calendar':
        return await this.refreshGoogleToken(refreshToken);
      default:
        return null;
    }
  }

  /**
   * Refresh Slack token
   */
  private async refreshSlackToken(
    refreshToken: string
  ): Promise<{ accessToken: string; refreshToken?: string; expiresIn: number } | null> {
    try {
      const response = await fetch('https://slack.com/api/oauth.v2.access', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          client_id: process.env.SLACK_CLIENT_ID!,
          client_secret: process.env.SLACK_CLIENT_SECRET!,
          grant_type: 'refresh_token',
          refresh_token: refreshToken,
        }),
      });

      const data = await response.json() as any;

      if (data.ok) {
        return {
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
          expiresIn: data.expires_in || 43200, // 12 hours default
        };
      }

      logger.error('Slack token refresh failed', { error: data.error });
      return null;
    } catch (error) {
      logger.error('Slack token refresh error', { error });
      return null;
    }
  }

  /**
   * Refresh Google token (Gmail/Calendar)
   */
  private async refreshGoogleToken(
    refreshToken: string
  ): Promise<{ accessToken: string; expiresIn: number } | null> {
    try {
      const response = await fetch('https://oauth2.googleapis.com/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          client_id: process.env.GMAIL_CLIENT_ID!,
          client_secret: process.env.GMAIL_CLIENT_SECRET!,
          grant_type: 'refresh_token',
          refresh_token: refreshToken,
        }),
      });

      const data = await response.json() as any;

      if (data.access_token) {
        return {
          accessToken: data.access_token,
          expiresIn: data.expires_in || 3600, // 1 hour default
        };
      }

      logger.error('Google token refresh failed', { error: data.error });
      return null;
    } catch (error) {
      logger.error('Google token refresh error', { error });
      return null;
    }
  }

  /**
   * Delete OAuth token for a user
   */
  async deleteToken(userId: string, service: 'slack' | 'gmail' | 'calendar'): Promise<void> {
    try {
      const docId = `${userId}_${service}`;
      await this.firestore.collection(this.COLLECTION).doc(docId).delete();

      logger.info('OAuth token deleted', { userId, service });
    } catch (error) {
      logger.error('Failed to delete OAuth token', { error, userId, service });
      throw error;
    }
  }

  /**
   * List all tokens for a user
   */
  async listUserTokens(userId: string): Promise<Array<{ service: string; expiresAt?: Date }>> {
    try {
      const snapshot = await this.firestore
        .collection(this.COLLECTION)
        .where('userId', '==', userId)
        .get();

      return snapshot.docs.map((doc) => {
        const data = doc.data();
        return {
          service: data.service,
          expiresAt: data.expiresAt?.toDate(),
        };
      });
    } catch (error) {
      logger.error('Failed to list user tokens', { error, userId });
      throw error;
    }
  }

  /**
   * Check if user has valid token for service
   */
  async hasValidToken(userId: string, service: 'slack' | 'gmail' | 'calendar'): Promise<boolean> {
    const token = await this.getToken(userId, service);
    return token !== null;
  }

  /**
   * Encrypt token using AES-256-GCM
   */
  private encrypt(text: string): string {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv(
      'aes-256-gcm',
      Buffer.from(this.encryptionKey, 'hex'),
      iv
    );

    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');

    const authTag = cipher.getAuthTag();

    // Return: iv:authTag:encrypted
    return `${iv.toString('hex')}:${authTag.toString('hex')}:${encrypted}`;
  }

  /**
   * Decrypt token
   */
  private decrypt(encryptedData: string): string {
    const parts = encryptedData.split(':');
    if (parts.length !== 3) {
      throw new Error('Invalid encrypted data format');
    }

    const iv = Buffer.from(parts[0], 'hex');
    const authTag = Buffer.from(parts[1], 'hex');
    const encrypted = parts[2];

    const decipher = crypto.createDecipheriv(
      'aes-256-gcm',
      Buffer.from(this.encryptionKey, 'hex'),
      iv
    );
    decipher.setAuthTag(authTag);

    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');

    return decrypted;
  }

  /**
   * Generate encryption key (32 bytes for AES-256)
   */
  private generateEncryptionKey(): string {
    return crypto.randomBytes(32).toString('hex');
  }
}

// Singleton instance
export const tokenManager = new TokenManager();
