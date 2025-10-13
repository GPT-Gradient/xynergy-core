import { WebClient } from '@slack/web-api';
import { Firestore } from '@google-cloud/firestore';
import * as crypto from 'crypto';
import { appConfig } from '../config/config';
import { logger } from '../utils/logger';
import { ServiceUnavailableError } from '../middleware/errorHandler';

/**
 * Slack Service - Manages Slack API interactions
 * NOTE: Uses per-user OAuth tokens from Firestore
 */
export class SlackService {
  private firestore: Firestore;
  private isMockMode: boolean = false;
  private encryptionKey: string;

  constructor() {
    this.firestore = new Firestore();
    this.encryptionKey = process.env.TOKEN_ENCRYPTION_KEY || crypto.randomBytes(32).toString('hex');
    this.initialize();
  }

  private initialize(): void {
    // Check if OAuth credentials are configured
    if (!appConfig.slack.clientId || !appConfig.slack.clientSecret) {
      logger.warn('Slack OAuth not configured - running in MOCK MODE');
      this.isMockMode = true;
    } else {
      logger.info('Slack service initialized with OAuth support');
      this.isMockMode = false;
    }
  }

  /**
   * Get user-specific Slack client with their OAuth token
   */
  private async getUserClient(userId: string): Promise<WebClient> {
    // Check if mock mode
    if (this.isMockMode) {
      throw new ServiceUnavailableError('Slack not configured. Please contact administrator.');
    }

    try {
      // Retrieve user's OAuth token from Firestore
      const tokenDoc = await this.firestore
        .collection('oauth_tokens')
        .doc(`${userId}_slack`)
        .get();

      if (!tokenDoc.exists) {
        throw new ServiceUnavailableError('Slack not connected. Please connect your Slack account in Settings > Integrations.');
      }

      const tokenData = tokenDoc.data();

      // Check token expiry
      if (tokenData?.expiresAt && new Date() >= tokenData.expiresAt.toDate()) {
        logger.warn('Slack token expired', { userId });
        throw new ServiceUnavailableError('Slack token expired. Please reconnect your Slack account in Settings > Integrations.');
      }

      // Decrypt access token
      const accessToken = this.decrypt(tokenData?.accessToken);

      // Create user-specific client
      return new WebClient(accessToken);
    } catch (error: any) {
      logger.error('Failed to get user Slack client', { error: error.message, userId });
      throw error;
    }
  }

  /**
   * Decrypt token using AES-256-GCM
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
   * Check if service is in mock mode
   */
  public isInMockMode(): boolean {
    return this.isMockMode;
  }

  /**
   * Test Slack API connection
   */
  async testConnection(userId: string): Promise<{ ok: boolean; team?: string; error?: string }> {
    if (this.isMockMode) {
      return {
        ok: true,
        team: 'Mock Workspace (No credentials configured)',
      };
    }

    try {
      const client = await this.getUserClient(userId);
      const result = await client.auth.test();
      return {
        ok: true,
        team: result.team as string,
      };
    } catch (error: any) {
      logger.error('Slack connection test failed', { error: error.message, userId });
      return {
        ok: false,
        error: error.message,
      };
    }
  }

  /**
   * List channels in workspace
   */
  async listChannels(userId: string): Promise<any[]> {
    if (this.isMockMode) {
      return this.getMockChannels();
    }

    try {
      const client = await this.getUserClient(userId);
      const result = await client.conversations.list({
        types: 'public_channel,private_channel',
        limit: 100,
      });

      return result.channels || [];
    } catch (error: any) {
      logger.error('Failed to list Slack channels', { error: error.message, userId });
      throw new ServiceUnavailableError('Failed to fetch Slack channels');
    }
  }

  /**
   * Get channel history
   */
  async getChannelHistory(userId: string, channelId: string, limit: number = 20): Promise<any[]> {
    if (this.isMockMode) {
      return this.getMockMessages(channelId, limit);
    }

    try {
      const client = await this.getUserClient(userId);
      const result = await client.conversations.history({
        channel: channelId,
        limit,
      });

      return result.messages || [];
    } catch (error: any) {
      logger.error('Failed to fetch channel history', {
        channelId,
        userId,
        error: error.message,
      });
      throw new ServiceUnavailableError('Failed to fetch channel history');
    }
  }

  /**
   * Post message to channel
   */
  async postMessage(userId: string, channelId: string, text: string, blocks?: any[]): Promise<any> {
    if (this.isMockMode) {
      return this.getMockMessageResponse(channelId, text);
    }

    try {
      const client = await this.getUserClient(userId);
      const result = await client.chat.postMessage({
        channel: channelId,
        text,
        blocks,
      });

      return result;
    } catch (error: any) {
      logger.error('Failed to post Slack message', {
        channelId,
        userId,
        error: error.message,
      });
      throw new ServiceUnavailableError('Failed to post message to Slack');
    }
  }

  /**
   * Search messages
   */
  async searchMessages(userId: string, query: string, count: number = 20): Promise<any> {
    if (this.isMockMode) {
      return this.getMockSearchResults(query, count);
    }

    try {
      const client = await this.getUserClient(userId);
      const result = await client.search.messages({
        query,
        count,
        sort: 'timestamp',
        sort_dir: 'desc',
      });

      return result;
    } catch (error: any) {
      logger.error('Failed to search Slack messages', {
        query,
        userId,
        error: error.message,
      });
      throw new ServiceUnavailableError('Failed to search Slack messages');
    }
  }

  /**
   * Get user info
   */
  async getUserInfo(requestingUserId: string, slackUserId: string): Promise<any> {
    if (this.isMockMode) {
      return this.getMockUser(slackUserId);
    }

    try {
      const client = await this.getUserClient(requestingUserId);
      const result = await client.users.info({
        user: slackUserId,
      });

      return result.user;
    } catch (error: any) {
      logger.error('Failed to get Slack user info', {
        slackUserId,
        requestingUserId,
        error: error.message,
      });
      throw new ServiceUnavailableError('Failed to fetch user info');
    }
  }

  /**
   * List users in workspace
   */
  async listUsers(userId: string): Promise<any[]> {
    if (this.isMockMode) {
      return this.getMockUsers();
    }

    try {
      const client = await this.getUserClient(userId);
      const result = await client.users.list({
        limit: 100,
      });

      return result.members || [];
    } catch (error: any) {
      logger.error('Failed to list Slack users', { error: error.message, userId });
      throw new ServiceUnavailableError('Failed to fetch Slack users');
    }
  }

  // ========== MOCK DATA METHODS ==========

  private getMockChannels(): any[] {
    return [
      {
        id: 'C001',
        name: 'general',
        is_channel: true,
        is_private: false,
        num_members: 42,
        topic: { value: 'Company-wide announcements' },
        purpose: { value: 'General discussion' },
      },
      {
        id: 'C002',
        name: 'engineering',
        is_channel: true,
        is_private: false,
        num_members: 15,
        topic: { value: 'Engineering team channel' },
        purpose: { value: 'Technical discussions' },
      },
      {
        id: 'C003',
        name: 'marketing',
        is_channel: true,
        is_private: false,
        num_members: 8,
        topic: { value: 'Marketing team channel' },
        purpose: { value: 'Marketing campaigns and strategy' },
      },
    ];
  }

  private getMockMessages(channelId: string, limit: number): any[] {
    const messages = [];
    for (let i = 0; i < Math.min(limit, 10); i++) {
      messages.push({
        type: 'message',
        user: `U00${i % 3}`,
        text: `Mock message ${i + 1} in channel ${channelId}`,
        ts: (Date.now() / 1000 - i * 3600).toString(),
      });
    }
    return messages;
  }

  private getMockMessageResponse(channelId: string, text: string): any {
    return {
      ok: true,
      channel: channelId,
      ts: (Date.now() / 1000).toString(),
      message: {
        type: 'message',
        user: 'U_BOT',
        text,
        ts: (Date.now() / 1000).toString(),
      },
    };
  }

  private getMockSearchResults(query: string, count: number): any {
    return {
      ok: true,
      query,
      messages: {
        total: 5,
        matches: [
          {
            type: 'message',
            user: 'U001',
            text: `Mock search result for "${query}"`,
            ts: (Date.now() / 1000).toString(),
            channel: { id: 'C001', name: 'general' },
          },
        ],
      },
    };
  }

  private getMockUser(userId: string): any {
    return {
      id: userId,
      name: `mock_user_${userId}`,
      real_name: `Mock User ${userId}`,
      profile: {
        email: `${userId}@example.com`,
        image_48: 'https://via.placeholder.com/48',
      },
      is_bot: false,
    };
  }

  private getMockUsers(): any[] {
    return [
      {
        id: 'U001',
        name: 'alice',
        real_name: 'Alice Johnson',
        profile: { email: 'alice@example.com', image_48: 'https://via.placeholder.com/48' },
        is_bot: false,
      },
      {
        id: 'U002',
        name: 'bob',
        real_name: 'Bob Smith',
        profile: { email: 'bob@example.com', image_48: 'https://via.placeholder.com/48' },
        is_bot: false,
      },
      {
        id: 'U003',
        name: 'charlie',
        real_name: 'Charlie Brown',
        profile: { email: 'charlie@example.com', image_48: 'https://via.placeholder.com/48' },
        is_bot: false,
      },
    ];
  }
}

// Singleton instance
export const slackService = new SlackService();
