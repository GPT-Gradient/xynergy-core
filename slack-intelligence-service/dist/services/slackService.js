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
exports.slackService = exports.SlackService = void 0;
const web_api_1 = require("@slack/web-api");
const firestore_1 = require("@google-cloud/firestore");
const crypto = __importStar(require("crypto"));
const config_1 = require("../config/config");
const logger_1 = require("../utils/logger");
const errorHandler_1 = require("../middleware/errorHandler");
/**
 * Slack Service - Manages Slack API interactions
 * NOTE: Uses per-user OAuth tokens from Firestore
 */
class SlackService {
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
        if (!config_1.appConfig.slack.clientId || !config_1.appConfig.slack.clientSecret) {
            logger_1.logger.warn('Slack OAuth not configured - running in MOCK MODE');
            this.isMockMode = true;
        }
        else {
            logger_1.logger.info('Slack service initialized with OAuth support');
            this.isMockMode = false;
        }
    }
    /**
     * Get user-specific Slack client with their OAuth token
     */
    async getUserClient(userId) {
        // Check if mock mode
        if (this.isMockMode) {
            throw new errorHandler_1.ServiceUnavailableError('Slack not configured. Please contact administrator.');
        }
        try {
            // Retrieve user's OAuth token from Firestore
            const tokenDoc = await this.firestore
                .collection('oauth_tokens')
                .doc(`${userId}_slack`)
                .get();
            if (!tokenDoc.exists) {
                throw new errorHandler_1.ServiceUnavailableError('Slack not connected. Please connect your Slack account in Settings > Integrations.');
            }
            const tokenData = tokenDoc.data();
            // Check token expiry
            if (tokenData?.expiresAt && new Date() >= tokenData.expiresAt.toDate()) {
                logger_1.logger.warn('Slack token expired', { userId });
                throw new errorHandler_1.ServiceUnavailableError('Slack token expired. Please reconnect your Slack account in Settings > Integrations.');
            }
            // Decrypt access token
            const accessToken = this.decrypt(tokenData?.accessToken);
            // Create user-specific client
            return new web_api_1.WebClient(accessToken);
        }
        catch (error) {
            logger_1.logger.error('Failed to get user Slack client', { error: error.message, userId });
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
     * Test Slack API connection
     */
    async testConnection(userId) {
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
                team: result.team,
            };
        }
        catch (error) {
            logger_1.logger.error('Slack connection test failed', { error: error.message, userId });
            return {
                ok: false,
                error: error.message,
            };
        }
    }
    /**
     * List channels in workspace
     */
    async listChannels(userId) {
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
        }
        catch (error) {
            logger_1.logger.error('Failed to list Slack channels', { error: error.message, userId });
            throw new errorHandler_1.ServiceUnavailableError('Failed to fetch Slack channels');
        }
    }
    /**
     * Get channel history
     */
    async getChannelHistory(userId, channelId, limit = 20) {
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
        }
        catch (error) {
            logger_1.logger.error('Failed to fetch channel history', {
                channelId,
                userId,
                error: error.message,
            });
            throw new errorHandler_1.ServiceUnavailableError('Failed to fetch channel history');
        }
    }
    /**
     * Post message to channel
     */
    async postMessage(userId, channelId, text, blocks) {
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
        }
        catch (error) {
            logger_1.logger.error('Failed to post Slack message', {
                channelId,
                userId,
                error: error.message,
            });
            throw new errorHandler_1.ServiceUnavailableError('Failed to post message to Slack');
        }
    }
    /**
     * Search messages
     */
    async searchMessages(userId, query, count = 20) {
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
        }
        catch (error) {
            logger_1.logger.error('Failed to search Slack messages', {
                query,
                userId,
                error: error.message,
            });
            throw new errorHandler_1.ServiceUnavailableError('Failed to search Slack messages');
        }
    }
    /**
     * Get user info
     */
    async getUserInfo(requestingUserId, slackUserId) {
        if (this.isMockMode) {
            return this.getMockUser(slackUserId);
        }
        try {
            const client = await this.getUserClient(requestingUserId);
            const result = await client.users.info({
                user: slackUserId,
            });
            return result.user;
        }
        catch (error) {
            logger_1.logger.error('Failed to get Slack user info', {
                slackUserId,
                requestingUserId,
                error: error.message,
            });
            throw new errorHandler_1.ServiceUnavailableError('Failed to fetch user info');
        }
    }
    /**
     * List users in workspace
     */
    async listUsers(userId) {
        if (this.isMockMode) {
            return this.getMockUsers();
        }
        try {
            const client = await this.getUserClient(userId);
            const result = await client.users.list({
                limit: 100,
            });
            return result.members || [];
        }
        catch (error) {
            logger_1.logger.error('Failed to list Slack users', { error: error.message, userId });
            throw new errorHandler_1.ServiceUnavailableError('Failed to fetch Slack users');
        }
    }
    // ========== MOCK DATA METHODS ==========
    getMockChannels() {
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
    getMockMessages(channelId, limit) {
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
    getMockMessageResponse(channelId, text) {
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
    getMockSearchResults(query, count) {
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
    getMockUser(userId) {
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
    getMockUsers() {
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
exports.SlackService = SlackService;
// Singleton instance
exports.slackService = new SlackService();
//# sourceMappingURL=slackService.js.map