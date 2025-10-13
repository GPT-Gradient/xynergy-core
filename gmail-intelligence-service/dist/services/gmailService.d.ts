/**
 * Gmail Service - Manages Gmail API interactions
 * NOTE: Uses per-user OAuth tokens from Firestore
 */
export declare class GmailService {
    private firestore;
    private isMockMode;
    private encryptionKey;
    constructor();
    private initialize;
    /**
     * Get user-specific Gmail client with their OAuth token
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
     * Test Gmail API connection
     */
    testConnection(userId: string): Promise<{
        ok: boolean;
        email?: string;
        error?: string;
    }>;
    /**
     * List messages in inbox
     */
    listMessages(userId: string, maxResults?: number, query?: string): Promise<any[]>;
    /**
     * Get message details
     */
    getMessage(userId: string, messageId: string): Promise<any>;
    /**
     * Send email
     */
    sendMessage(userId: string, to: string, subject: string, body: string, cc?: string[], bcc?: string[]): Promise<any>;
    /**
     * Search messages
     */
    searchMessages(userId: string, query: string, maxResults?: number): Promise<any[]>;
    /**
     * Get thread
     */
    getThread(userId: string, threadId: string): Promise<any>;
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