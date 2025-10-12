/**
 * Slack Service - Manages Slack API interactions
 * NOTE: This service uses mock data when Slack credentials are not configured
 */
export declare class SlackService {
    private client;
    private isMockMode;
    constructor();
    private initialize;
    /**
     * Check if service is in mock mode
     */
    isInMockMode(): boolean;
    /**
     * Test Slack API connection
     */
    testConnection(): Promise<{
        ok: boolean;
        team?: string;
        error?: string;
    }>;
    /**
     * List channels in workspace
     */
    listChannels(): Promise<any[]>;
    /**
     * Get channel history
     */
    getChannelHistory(channelId: string, limit?: number): Promise<any[]>;
    /**
     * Post message to channel
     */
    postMessage(channelId: string, text: string, blocks?: any[]): Promise<any>;
    /**
     * Search messages
     */
    searchMessages(query: string, count?: number): Promise<any>;
    /**
     * Get user info
     */
    getUserInfo(userId: string): Promise<any>;
    /**
     * List users in workspace
     */
    listUsers(): Promise<any[]>;
    private getMockChannels;
    private getMockMessages;
    private getMockMessageResponse;
    private getMockSearchResults;
    private getMockUser;
    private getMockUsers;
}
export declare const slackService: SlackService;
//# sourceMappingURL=slackService.d.ts.map