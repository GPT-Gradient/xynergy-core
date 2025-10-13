import { google } from 'googleapis';
import { Firestore } from '@google-cloud/firestore';
import * as crypto from 'crypto';
import { appConfig } from '../config';
import { logger } from '../utils/logger';
import { ServiceUnavailableError } from '../middleware/errorHandler';

/**
 * Gmail Service - Manages Gmail API interactions
 * NOTE: Uses per-user OAuth tokens from Firestore
 */
export class GmailService {
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
    if (!appConfig.gmail.clientId || !appConfig.gmail.clientSecret) {
      logger.warn('Gmail OAuth not configured - running in MOCK MODE');
      this.isMockMode = true;
    } else {
      logger.info('Gmail service initialized with OAuth support');
      this.isMockMode = false;
    }
  }

  /**
   * Get user-specific Gmail client with their OAuth token
   */
  private async getUserClient(userId: string): Promise<any> {
    // Check if mock mode
    if (this.isMockMode) {
      throw new ServiceUnavailableError('Gmail not configured. Please contact administrator.');
    }

    try {
      // Retrieve user's OAuth token from Firestore
      const tokenDoc = await this.firestore
        .collection('oauth_tokens')
        .doc(`${userId}_gmail`)
        .get();

      if (!tokenDoc.exists) {
        throw new ServiceUnavailableError('Gmail not connected. Please connect your Gmail account in Settings > Integrations.');
      }

      const tokenData = tokenDoc.data();

      // Check token expiry
      if (tokenData?.expiresAt && new Date() >= tokenData.expiresAt.toDate()) {
        logger.warn('Gmail token expired', { userId });
        throw new ServiceUnavailableError('Gmail token expired. Please reconnect your Gmail account in Settings > Integrations.');
      }

      // Decrypt access token
      const accessToken = this.decrypt(tokenData?.accessToken);

      // Create user-specific OAuth client
      const oauth2Client = new google.auth.OAuth2(
        appConfig.gmail.clientId,
        appConfig.gmail.clientSecret,
        appConfig.gmail.redirectUri
      );

      oauth2Client.setCredentials({ access_token: accessToken });

      // Return Gmail API client
      return google.gmail({ version: 'v1', auth: oauth2Client });
    } catch (error: any) {
      logger.error('Failed to get user Gmail client', { error: error.message, userId });
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
   * Test Gmail API connection
   */
  async testConnection(userId: string): Promise<{ ok: boolean; email?: string; error?: string }> {
    if (this.isMockMode) {
      return {
        ok: true,
        email: 'mock@example.com (No credentials configured)',
      };
    }

    try {
      const gmail = await this.getUserClient(userId);
      const profile = await gmail.users.getProfile({ userId: 'me' });
      return {
        ok: true,
        email: profile.data.emailAddress,
      };
    } catch (error: any) {
      logger.error('Gmail connection test failed', { error: error.message, userId });
      return {
        ok: false,
        error: error.message,
      };
    }
  }

  /**
   * List messages in inbox
   */
  async listMessages(userId: string, maxResults: number = 20, query?: string): Promise<any[]> {
    if (this.isMockMode) {
      return this.getMockMessages(maxResults);
    }

    try {
      const gmail = await this.getUserClient(userId);
      const response = await gmail.users.messages.list({
        userId: 'me',
        maxResults,
        q: query,
      });

      return response.data.messages || [];
    } catch (error: any) {
      logger.error('Failed to list Gmail messages', { error: error.message, userId });
      throw new ServiceUnavailableError('Failed to fetch Gmail messages');
    }
  }

  /**
   * Get message details
   */
  async getMessage(userId: string, messageId: string): Promise<any> {
    if (this.isMockMode) {
      return this.getMockMessageDetails(messageId);
    }

    try {
      const gmail = await this.getUserClient(userId);
      const response = await gmail.users.messages.get({
        userId: 'me',
        id: messageId,
        format: 'full',
      });

      return this.parseMessage(response.data);
    } catch (error: any) {
      logger.error('Failed to get Gmail message', { messageId, userId, error: error.message });
      throw new ServiceUnavailableError('Failed to fetch message');
    }
  }

  /**
   * Send email
   */
  async sendMessage(userId: string, to: string, subject: string, body: string, cc?: string[], bcc?: string[]): Promise<any> {
    if (this.isMockMode) {
      return this.getMockSentMessage(to, subject);
    }

    try {
      const gmail = await this.getUserClient(userId);
      const email = this.createEmailMessage(to, subject, body, cc, bcc);
      const response = await gmail.users.messages.send({
        userId: 'me',
        requestBody: {
          raw: email,
        },
      });

      return response.data;
    } catch (error: any) {
      logger.error('Failed to send Gmail message', { to, subject, userId, error: error.message });
      throw new ServiceUnavailableError('Failed to send email');
    }
  }

  /**
   * Search messages
   */
  async searchMessages(userId: string, query: string, maxResults: number = 20): Promise<any[]> {
    if (this.isMockMode) {
      return this.getMockSearchResults(query, maxResults);
    }

    return this.listMessages(userId, maxResults, query);
  }

  /**
   * Get thread
   */
  async getThread(userId: string, threadId: string): Promise<any> {
    if (this.isMockMode) {
      return this.getMockThread(threadId);
    }

    try {
      const gmail = await this.getUserClient(userId);
      const response = await gmail.users.threads.get({
        userId: 'me',
        id: threadId,
      });

      return response.data;
    } catch (error: any) {
      logger.error('Failed to get Gmail thread', { threadId, userId, error: error.message });
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
