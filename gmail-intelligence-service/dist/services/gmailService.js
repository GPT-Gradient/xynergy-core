"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.gmailService = exports.GmailService = void 0;
const googleapis_1 = require("googleapis");
const firestore_1 = require("@google-cloud/firestore");
const crypto = __importStar(require("crypto"));
const config_1 = require("../config");
const logger_1 = require("../utils/logger");
const errorHandler_1 = require("../middleware/errorHandler");
/**
 * Gmail Service - Manages Gmail API interactions
 * NOTE: Uses per-user OAuth tokens from Firestore
 */
class GmailService {
    firestore;
    isMockMode = false;
    encryptionKey;
    constructor() {
        this.firestore = new firestore_1.Firestore();
        this.encryptionKey = process.env.TOKEN_ENCRYPTION_KEY || crypto.randomBytes(32).toString('hex');
        this.initialize();
    }
    initialize() {
        // Check if OAuth credentials are configured
        if (!config_1.appConfig.gmail.clientId || !config_1.appConfig.gmail.clientSecret) {
            logger_1.logger.warn('Gmail OAuth not configured - running in MOCK MODE');
            this.isMockMode = true;
        }
        else {
            logger_1.logger.info('Gmail service initialized with OAuth support');
            this.isMockMode = false;
        }
    }
    /**
     * Get user-specific Gmail client with their OAuth token
     */
    async getUserClient(userId) {
        // Check if mock mode
        if (this.isMockMode) {
            throw new errorHandler_1.ServiceUnavailableError('Gmail not configured. Please contact administrator.');
        }
        try {
            // Retrieve user's OAuth token from Firestore
            const tokenDoc = await this.firestore
                .collection('oauth_tokens')
                .doc(`${userId}_gmail`)
                .get();
            if (!tokenDoc.exists) {
                throw new errorHandler_1.ServiceUnavailableError('Gmail not connected. Please connect your Gmail account in Settings > Integrations.');
            }
            const tokenData = tokenDoc.data();
            // Check token expiry
            if (tokenData?.expiresAt && new Date() >= tokenData.expiresAt.toDate()) {
                logger_1.logger.warn('Gmail token expired', { userId });
                throw new errorHandler_1.ServiceUnavailableError('Gmail token expired. Please reconnect your Gmail account in Settings > Integrations.');
            }
            // Decrypt access token
            const accessToken = this.decrypt(tokenData?.accessToken);
            // Create user-specific OAuth client
            const oauth2Client = new googleapis_1.google.auth.OAuth2(config_1.appConfig.gmail.clientId, config_1.appConfig.gmail.clientSecret, config_1.appConfig.gmail.redirectUri);
            oauth2Client.setCredentials({ access_token: accessToken });
            // Return Gmail API client
            return googleapis_1.google.gmail({ version: 'v1', auth: oauth2Client });
        }
        catch (error) {
            logger_1.logger.error('Failed to get user Gmail client', { error: error.message, userId });
            throw error;
        }
    }
    /**
     * Decrypt token using AES-256-GCM
     */
    decrypt(encryptedData) {
        const parts = encryptedData.split(':');
        if (parts.length !== 3) {
            throw new Error('Invalid encrypted data format');
        }
        const iv = Buffer.from(parts[0], 'hex');
        const authTag = Buffer.from(parts[1], 'hex');
        const encrypted = parts[2];
        const decipher = crypto.createDecipheriv('aes-256-gcm', Buffer.from(this.encryptionKey, 'hex'), iv);
        decipher.setAuthTag(authTag);
        let decrypted = decipher.update(encrypted, 'hex', 'utf8');
        decrypted += decipher.final('utf8');
        return decrypted;
    }
    /**
     * Check if service is in mock mode
     */
    isInMockMode() {
        return this.isMockMode;
    }
    /**
     * Test Gmail API connection
     */
    async testConnection(userId) {
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
        }
        catch (error) {
            logger_1.logger.error('Gmail connection test failed', { error: error.message, userId });
            return {
                ok: false,
                error: error.message,
            };
        }
    }
    /**
     * List messages in inbox
     */
    async listMessages(userId, maxResults = 20, query) {
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
        }
        catch (error) {
            logger_1.logger.error('Failed to list Gmail messages', { error: error.message, userId });
            throw new errorHandler_1.ServiceUnavailableError('Failed to fetch Gmail messages');
        }
    }
    /**
     * Get message details
     */
    async getMessage(userId, messageId) {
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
        }
        catch (error) {
            logger_1.logger.error('Failed to get Gmail message', { messageId, userId, error: error.message });
            throw new errorHandler_1.ServiceUnavailableError('Failed to fetch message');
        }
    }
    /**
     * Send email
     */
    async sendMessage(userId, to, subject, body, cc, bcc) {
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
        }
        catch (error) {
            logger_1.logger.error('Failed to send Gmail message', { to, subject, userId, error: error.message });
            throw new errorHandler_1.ServiceUnavailableError('Failed to send email');
        }
    }
    /**
     * Search messages
     */
    async searchMessages(userId, query, maxResults = 20) {
        if (this.isMockMode) {
            return this.getMockSearchResults(query, maxResults);
        }
        return this.listMessages(userId, maxResults, query);
    }
    /**
     * Get thread
     */
    async getThread(userId, threadId) {
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
        }
        catch (error) {
            logger_1.logger.error('Failed to get Gmail thread', { threadId, userId, error: error.message });
            throw new errorHandler_1.ServiceUnavailableError('Failed to fetch thread');
        }
    }
    /**
     * Parse Gmail message to friendly format
     */
    parseMessage(message) {
        const headers = message.payload?.headers || [];
        const getHeader = (name) => headers.find((h) => h.name.toLowerCase() === name.toLowerCase())?.value;
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
    getMessageBody(payload) {
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
    createEmailMessage(to, subject, body, cc, bcc) {
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
    getMockMessages(maxResults) {
        const messages = [];
        for (let i = 0; i < Math.min(maxResults, 10); i++) {
            messages.push({
                id: `msg_${i + 1}`,
                threadId: `thread_${Math.floor(i / 2) + 1}`,
            });
        }
        return messages;
    }
    getMockMessageDetails(messageId) {
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
    getMockSentMessage(to, subject) {
        return {
            id: `msg_sent_${Date.now()}`,
            threadId: `thread_sent_${Date.now()}`,
            labelIds: ['SENT'],
        };
    }
    getMockSearchResults(query, maxResults) {
        return [
            {
                id: 'msg_search_1',
                threadId: 'thread_search_1',
            },
        ];
    }
    getMockThread(threadId) {
        return {
            id: threadId,
            messages: [
                this.getMockMessageDetails('msg_1'),
                this.getMockMessageDetails('msg_2'),
            ],
        };
    }
}
exports.GmailService = GmailService;
exports.gmailService = new GmailService();
//# sourceMappingURL=gmailService.js.map