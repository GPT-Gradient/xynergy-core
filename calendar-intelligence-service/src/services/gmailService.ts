import { google } from 'googleapis';
import { logger } from '../utils/logger';
import { ServiceUnavailableError } from '../middleware/errorHandler';

/**
 * Gmail Service - Manages Gmail API interactions
 * NOTE: This service uses mock data when Gmail credentials are not configured
 */
export class GmailService {
  private gmail: any = null;
  private isMockMode: boolean = false;

  constructor() {
    this.initialize();
  }

  private initialize(): void {
    // For now, always use mock mode until OAuth is configured
    // TODO: Implement OAuth flow for production use
    logger.warn('Gmail credentials not configured - running in MOCK MODE');
    this.isMockMode = true;
  }

  /**
   * Check if service is in mock mode
   */
  public isInMockMode(): boolean {
    return this.isMockMode;
  }

  /**
   * Test Gmail API connection
   */
  async testConnection(): Promise<{ ok: boolean; email?: string; error?: string }> {
    if (this.isMockMode) {
      return {
        ok: true,
        email: 'mock@example.com (No credentials configured)',
      };
    }

    try {
      const profile = await this.gmail.users.getProfile({ userId: 'me' });
      return {
        ok: true,
        email: profile.data.emailAddress,
      };
    } catch (error: any) {
      logger.error('Gmail connection test failed', { error: error.message });
      return {
        ok: false,
        error: error.message,
      };
    }
  }

  /**
   * List messages in inbox
   */
  async listMessages(maxResults: number = 20, query?: string): Promise<any[]> {
    if (this.isMockMode) {
      return this.getMockMessages(maxResults);
    }

    try {
      const response = await this.gmail.users.messages.list({
        userId: 'me',
        maxResults,
        q: query,
      });

      return response.data.messages || [];
    } catch (error: any) {
      logger.error('Failed to list Gmail messages', { error: error.message });
      throw new ServiceUnavailableError('Failed to fetch Gmail messages');
    }
  }

  /**
   * Get message details
   */
  async getMessage(messageId: string): Promise<any> {
    if (this.isMockMode) {
      return this.getMockMessageDetails(messageId);
    }

    try {
      const response = await this.gmail.users.messages.get({
        userId: 'me',
        id: messageId,
        format: 'full',
      });

      return this.parseMessage(response.data);
    } catch (error: any) {
      logger.error('Failed to get Gmail message', { messageId, error: error.message });
      throw new ServiceUnavailableError('Failed to fetch message');
    }
  }

  /**
   * Send email
   */
  async sendMessage(to: string, subject: string, body: string, cc?: string[], bcc?: string[]): Promise<any> {
    if (this.isMockMode) {
      return this.getMockSentMessage(to, subject);
    }

    try {
      const email = this.createEmailMessage(to, subject, body, cc, bcc);
      const response = await this.gmail.users.messages.send({
        userId: 'me',
        requestBody: {
          raw: email,
        },
      });

      return response.data;
    } catch (error: any) {
      logger.error('Failed to send Gmail message', { to, subject, error: error.message });
      throw new ServiceUnavailableError('Failed to send email');
    }
  }

  /**
   * Search messages
   */
  async searchMessages(query: string, maxResults: number = 20): Promise<any[]> {
    if (this.isMockMode) {
      return this.getMockSearchResults(query, maxResults);
    }

    return this.listMessages(maxResults, query);
  }

  /**
   * Get thread
   */
  async getThread(threadId: string): Promise<any> {
    if (this.isMockMode) {
      return this.getMockThread(threadId);
    }

    try {
      const response = await this.gmail.users.threads.get({
        userId: 'me',
        id: threadId,
      });

      return response.data;
    } catch (error: any) {
      logger.error('Failed to get Gmail thread', { threadId, error: error.message });
      throw new ServiceUnavailableError('Failed to fetch thread');
    }
  }

  /**
   * Parse Gmail message to friendly format
   */
  private parseMessage(message: any): any {
    const headers = message.payload?.headers || [];
    const getHeader = (name: string) => headers.find((h: any) => h.name.toLowerCase() === name.toLowerCase())?.value;

    return {
      id: message.id,
      threadId: message.threadId,
      from: getHeader('from'),
      to: getHeader('to'),
      cc: getHeader('cc'),
      subject: getHeader('subject'),
      date: getHeader('date'),
      snippet: message.snippet,
      body: this.getMessageBody(message.payload),
      labelIds: message.labelIds || [],
    };
  }

  /**
   * Get message body from payload
   */
  private getMessageBody(payload: any): string {
    if (payload.body?.data) {
      return Buffer.from(payload.body.data, 'base64').toString('utf-8');
    }

    if (payload.parts) {
      for (const part of payload.parts) {
        if (part.mimeType === 'text/plain' && part.body?.data) {
          return Buffer.from(part.body.data, 'base64').toString('utf-8');
        }
      }
    }

    return '';
  }

  /**
   * Create email message for sending
   */
  private createEmailMessage(to: string, subject: string, body: string, cc?: string[], bcc?: string[]): string {
    const lines = [
      `To: ${to}`,
      cc && cc.length > 0 ? `Cc: ${cc.join(', ')}` : '',
      bcc && bcc.length > 0 ? `Bcc: ${bcc.join(', ')}` : '',
      `Subject: ${subject}`,
      '',
      body,
    ].filter(Boolean);

    const email = lines.join('\r\n');
    return Buffer.from(email).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  }

  // ========== MOCK DATA METHODS ==========

  private getMockMessages(maxResults: number): any[] {
    const messages = [];
    for (let i = 0; i < Math.min(maxResults, 10); i++) {
      messages.push({
        id: `msg_${i + 1}`,
        threadId: `thread_${Math.floor(i / 2) + 1}`,
      });
    }
    return messages;
  }

  private getMockMessageDetails(messageId: string): any {
    return {
      id: messageId,
      threadId: `thread_${messageId.slice(-1)}`,
      from: 'sender@example.com',
      to: 'mock@example.com',
      cc: null,
      subject: `Mock Email ${messageId}`,
      date: new Date().toISOString(),
      snippet: `This is a mock email message ${messageId} for testing purposes...`,
      body: `Hello,\n\nThis is a mock email body for message ${messageId}.\n\nBest regards,\nMock Sender`,
      labelIds: ['INBOX', 'UNREAD'],
    };
  }

  private getMockSentMessage(to: string, subject: string): any {
    return {
      id: `msg_sent_${Date.now()}`,
      threadId: `thread_sent_${Date.now()}`,
      labelIds: ['SENT'],
    };
  }

  private getMockSearchResults(query: string, maxResults: number): any[] {
    return [
      {
        id: 'msg_search_1',
        threadId: 'thread_search_1',
      },
    ];
  }

  private getMockThread(threadId: string): any {
    return {
      id: threadId,
      messages: [
        this.getMockMessageDetails('msg_1'),
        this.getMockMessageDetails('msg_2'),
      ],
    };
  }
}

export const gmailService = new GmailService();
