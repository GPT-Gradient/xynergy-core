/**
 * Slack Service - Manages Slack API interactions
 * NOTE: Uses per-user OAuth tokens from Firestore
 */
export declare class SlackService {
    private firestore;
    private isMockMode;
    private encryptionKey;
    constructor();
    private initialize;
    /**
     * Get user-specific Slack client with their OAuth token
     */
    private getUserClient;
    /**
     * Decrypt token using AES-256-GCM
     */
    private decrypt;
    /**
     * Check if service is in mock mode
     */
    isInMockMode(): boolean;
    /**
     * Test Slack API connection
     */
    testConnection(userId: string): Promise<{
        ok: boolean;
        team?: string;
        error?: string;
    }>;
    /**
     * List channels in workspace
     */
    listChannels(userId: string): Promise<any[]>;
    /**
     * Get channel history
     */
    getChannelHistory(userId: string, channelId: string, limit?: number): Promise<any[]>;
    /**
     * Post message to channel
     */
    postMessage(userId: string, channelId: string, text: string, blocks?: any[]): Promise<any>;
    /**
     * Search messages
     */
    searchMessages(userId: string, query: string, count?: number): Promise<any>;
    /**
     * Get user info
     */
    getUserInfo(requestingUserId: string, slackUserId: string): Promise<any>;
    /**
     * List users in workspace
     */
    listUsers(userId: string): Promise<any[]>;
    private getMockChannels;
    private getMockMessages;
    private getMockMessageResponse;
    private getMockSearchResults;
    private getMockUser;
    private getMockUsers;
}
export declare const slackService: SlackService;
//# sourceMappingURL=slackService.d.ts.map