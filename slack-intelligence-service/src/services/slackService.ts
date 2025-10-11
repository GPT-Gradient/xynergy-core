import { WebClient } from '@slack/web-api';
import { appConfig } from '../config/config';
import { logger } from '../utils/logger';
import { ServiceUnavailableError } from '../middleware/errorHandler';

/**
 * Slack Service - Manages Slack API interactions
 * NOTE: This service uses mock data when Slack credentials are not configured
 */
export class SlackService {
  private client: WebClient | null = null;
  private isMockMode: boolean = false;

  constructor() {
    this.initialize();
  }

  private initialize(): void {
    if (appConfig.slack.botToken) {
      try {
        this.client = new WebClient(appConfig.slack.botToken);
        this.isMockMode = false;
        logger.info('Slack client initialized with bot token');
      } catch (error) {
        logger.error('Failed to initialize Slack client', { error });
        this.isMockMode = true;
      }
    } else {
      logger.warn('Slack bot token not configured - running in MOCK MODE');
      this.isMockMode = true;
    }
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
  async testConnection(): Promise<{ ok: boolean; team?: string; error?: string }> {
    if (this.isMockMode) {
      return {
        ok: true,
        team: 'Mock Workspace (No credentials configured)',
      };
    }

    try {
      const result = await this.client!.auth.test();
      return {
        ok: true,
        team: result.team as string,
      };
    } catch (error: any) {
      logger.error('Slack connection test failed', { error: error.message });
      return {
        ok: false,
        error: error.message,
      };
    }
  }

  /**
   * List channels in workspace
   */
  async listChannels(): Promise<any[]> {
    if (this.isMockMode) {
      return this.getMockChannels();
    }

    try {
      const result = await this.client!.conversations.list({
        types: 'public_channel,private_channel',
        limit: 100,
      });

      return result.channels || [];
    } catch (error: any) {
      logger.error('Failed to list Slack channels', { error: error.message });
      throw new ServiceUnavailableError('Failed to fetch Slack channels');
    }
  }

  /**
   * Get channel history
   */
  async getChannelHistory(channelId: string, limit: number = 20): Promise<any[]> {
    if (this.isMockMode) {
      return this.getMockMessages(channelId, limit);
    }

    try {
      const result = await this.client!.conversations.history({
        channel: channelId,
        limit,
      });

      return result.messages || [];
    } catch (error: any) {
      logger.error('Failed to fetch channel history', {
        channelId,
        error: error.message,
      });
      throw new ServiceUnavailableError('Failed to fetch channel history');
    }
  }

  /**
   * Post message to channel
   */
  async postMessage(channelId: string, text: string, blocks?: any[]): Promise<any> {
    if (this.isMockMode) {
      return this.getMockMessageResponse(channelId, text);
    }

    try {
      const result = await this.client!.chat.postMessage({
        channel: channelId,
        text,
        blocks,
      });

      return result;
    } catch (error: any) {
      logger.error('Failed to post Slack message', {
        channelId,
        error: error.message,
      });
      throw new ServiceUnavailableError('Failed to post message to Slack');
    }
  }

  /**
   * Search messages
   */
  async searchMessages(query: string, count: number = 20): Promise<any> {
    if (this.isMockMode) {
      return this.getMockSearchResults(query, count);
    }

    try {
      const result = await this.client!.search.messages({
        query,
        count,
        sort: 'timestamp',
        sort_dir: 'desc',
      });

      return result;
    } catch (error: any) {
      logger.error('Failed to search Slack messages', {
        query,
        error: error.message,
      });
      throw new ServiceUnavailableError('Failed to search Slack messages');
    }
  }

  /**
   * Get user info
   */
  async getUserInfo(userId: string): Promise<any> {
    if (this.isMockMode) {
      return this.getMockUser(userId);
    }

    try {
      const result = await this.client!.users.info({
        user: userId,
      });

      return result.user;
    } catch (error: any) {
      logger.error('Failed to get Slack user info', {
        userId,
        error: error.message,
      });
      throw new ServiceUnavailableError('Failed to fetch user info');
    }
  }

  /**
   * List users in workspace
   */
  async listUsers(): Promise<any[]> {
    if (this.isMockMode) {
      return this.getMockUsers();
    }

    try {
      const result = await this.client!.users.list({
        limit: 100,
      });

      return result.members || [];
    } catch (error: any) {
      logger.error('Failed to list Slack users', { error: error.message });
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
