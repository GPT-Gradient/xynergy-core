/**
 * Gmail Service - Manages Gmail API interactions
 * NOTE: This service uses mock data when Gmail credentials are not configured
 */
export declare class GmailService {
    private gmail;
    private isMockMode;
    constructor();
    private initialize;
    /**
     * Check if service is in mock mode
     */
    isInMockMode(): boolean;
    /**
     * Test Gmail API connection
     */
    testConnection(): Promise<{
        ok: boolean;
        email?: string;
        error?: string;
    }>;
    /**
     * List messages in inbox
     */
    listMessages(maxResults?: number, query?: string): Promise<any[]>;
    /**
     * Get message details
     */
    getMessage(messageId: string): Promise<any>;
    /**
     * Send email
     */
    sendMessage(to: string, subject: string, body: string, cc?: string[], bcc?: string[]): Promise<any>;
    /**
     * Search messages
     */
    searchMessages(query: string, maxResults?: number): Promise<any[]>;
    /**
     * Get thread
     */
    getThread(threadId: string): Promise<any>;
    /**
     * Parse Gmail message to friendly format
     */
    private parseMessage;
    /**
     * Get message body from payload
     */
    private getMessageBody;
    /**
     * Create email message for sending
     */
    private createEmailMessage;
    private getMockMessages;
    private getMockMessageDetails;
    private getMockSentMessage;
    private getMockSearchResults;
    private getMockThread;
}
export declare const gmailService: GmailService;
//# sourceMappingURL=gmailService.d.ts.map