"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.slackService = exports.SlackService = void 0;
const web_api_1 = require("@slack/web-api");
const config_1 = require("../config/config");
const logger_1 = require("../utils/logger");
const errorHandler_1 = require("../middleware/errorHandler");
/**
 * Slack Service - Manages Slack API interactions
 * NOTE: This service uses mock data when Slack credentials are not configured
 */
class SlackService {
    client = null;
    isMockMode = false;
    constructor() {
        this.initialize();
    }
    initialize() {
        if (config_1.appConfig.slack.botToken) {
            try {
                this.client = new web_api_1.WebClient(config_1.appConfig.slack.botToken);
                this.isMockMode = false;
                logger_1.logger.info('Slack client initialized with bot token');
            }
            catch (error) {
                logger_1.logger.error('Failed to initialize Slack client', { error });
                this.isMockMode = true;
            }
        }
        else {
            logger_1.logger.warn('Slack bot token not configured - running in MOCK MODE');
            this.isMockMode = true;
        }
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
    async testConnection() {
        if (this.isMockMode) {
            return {
                ok: true,
                team: 'Mock Workspace (No credentials configured)',
            };
        }
        try {
            const result = await this.client.auth.test();
            return {
                ok: true,
                team: result.team,
            };
        }
        catch (error) {
            logger_1.logger.error('Slack connection test failed', { error: error.message });
            return {
                ok: false,
                error: error.message,
            };
        }
    }
    /**
     * List channels in workspace
     */
    async listChannels() {
        if (this.isMockMode) {
            return this.getMockChannels();
        }
        try {
            const result = await this.client.conversations.list({
                types: 'public_channel,private_channel',
                limit: 100,
            });
            return result.channels || [];
        }
        catch (error) {
            logger_1.logger.error('Failed to list Slack channels', { error: error.message });
            throw new errorHandler_1.ServiceUnavailableError('Failed to fetch Slack channels');
        }
    }
    /**
     * Get channel history
     */
    async getChannelHistory(channelId, limit = 20) {
        if (this.isMockMode) {
            return this.getMockMessages(channelId, limit);
        }
        try {
            const result = await this.client.conversations.history({
                channel: channelId,
                limit,
            });
            return result.messages || [];
        }
        catch (error) {
            logger_1.logger.error('Failed to fetch channel history', {
                channelId,
                error: error.message,
            });
            throw new errorHandler_1.ServiceUnavailableError('Failed to fetch channel history');
        }
    }
    /**
     * Post message to channel
     */
    async postMessage(channelId, text, blocks) {
        if (this.isMockMode) {
            return this.getMockMessageResponse(channelId, text);
        }
        try {
            const result = await this.client.chat.postMessage({
                channel: channelId,
                text,
                blocks,
            });
            return result;
        }
        catch (error) {
            logger_1.logger.error('Failed to post Slack message', {
                channelId,
                error: error.message,
            });
            throw new errorHandler_1.ServiceUnavailableError('Failed to post message to Slack');
        }
    }
    /**
     * Search messages
     */
    async searchMessages(query, count = 20) {
        if (this.isMockMode) {
            return this.getMockSearchResults(query, count);
        }
        try {
            const result = await this.client.search.messages({
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
                error: error.message,
            });
            throw new errorHandler_1.ServiceUnavailableError('Failed to search Slack messages');
        }
    }
    /**
     * Get user info
     */
    async getUserInfo(userId) {
        if (this.isMockMode) {
            return this.getMockUser(userId);
        }
        try {
            const result = await this.client.users.info({
                user: userId,
            });
            return result.user;
        }
        catch (error) {
            logger_1.logger.error('Failed to get Slack user info', {
                userId,
                error: error.message,
            });
            throw new errorHandler_1.ServiceUnavailableError('Failed to fetch user info');
        }
    }
    /**
     * List users in workspace
     */
    async listUsers() {
        if (this.isMockMode) {
            return this.getMockUsers();
        }
        try {
            const result = await this.client.users.list({
                limit: 100,
            });
            return result.members || [];
        }
        catch (error) {
            logger_1.logger.error('Failed to list Slack users', { error: error.message });
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