/**
 * Token Manager - Manages OAuth tokens for users
 *
 * Features:
 * - Store encrypted OAuth tokens per user
 * - Automatic token refresh
 * - Token expiry tracking
 * - Multi-service support (Slack, Gmail, Calendar)
 */
interface OAuthToken {
    userId: string;
    tenantId: string;
    service: 'slack' | 'gmail' | 'calendar';
    accessToken: string;
    refreshToken?: string;
    expiresAt?: Date;
    scopes: string[];
    metadata: Record<string, any>;
    createdAt: Date;
    updatedAt: Date;
}
export declare class TokenManager {
    private firestore;
    private encryptionKey;
    private readonly COLLECTION;
    constructor();
    /**
     * Store OAuth token for a user
     */
    storeToken(userId: string, tenantId: string, service: 'slack' | 'gmail' | 'calendar', accessToken: string, options?: {
        refreshToken?: string;
        expiresIn?: number;
        scopes?: string[];
        metadata?: Record<string, any>;
    }): Promise<void>;
    /**
     * Get OAuth token for a user
     */
    getToken(userId: string, service: 'slack' | 'gmail' | 'calendar'): Promise<OAuthToken | null>;
    /**
     * Refresh token if expired
     */
    private refreshTokenIfNeeded;
    /**
     * Refresh service-specific token
     */
    private refreshServiceToken;
    /**
     * Refresh Slack token
     */
    private refreshSlackToken;
    /**
     * Refresh Google token (Gmail/Calendar)
     */
    private refreshGoogleToken;
    /**
     * Delete OAuth token for a user
     */
    deleteToken(userId: string, service: 'slack' | 'gmail' | 'calendar'): Promise<void>;
    /**
     * List all tokens for a user
     */
    listUserTokens(userId: string): Promise<Array<{
        service: string;
        expiresAt?: Date;
    }>>;
    /**
     * Check if user has valid token for service
     */
    hasValidToken(userId: string, service: 'slack' | 'gmail' | 'calendar'): Promise<boolean>;
    /**
     * Encrypt token using AES-256-GCM
     */
    private encrypt;
    /**
     * Decrypt token
     */
    private decrypt;
    /**
     * Generate encryption key (32 bytes for AES-256)
     */
    private generateEncryptionKey;
}
export declare const tokenManager: TokenManager;
export {};
//# sourceMappingURL=tokenManager.d.ts.map