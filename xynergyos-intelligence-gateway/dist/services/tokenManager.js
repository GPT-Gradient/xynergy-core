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
exports.tokenManager = exports.TokenManager = void 0;
const firestore_1 = require("@google-cloud/firestore");
const logger_1 = require("../utils/logger");
const crypto = __importStar(require("crypto"));
class TokenManager {
    firestore;
    encryptionKey;
    COLLECTION = 'oauth_tokens';
    constructor() {
        this.firestore = new firestore_1.Firestore();
        // In production, load from Secret Manager
        this.encryptionKey = process.env.TOKEN_ENCRYPTION_KEY || this.generateEncryptionKey();
    }
    /**
     * Store OAuth token for a user
     */
    async storeToken(userId, tenantId, service, accessToken, options = {}) {
        try {
            const encryptedAccessToken = this.encrypt(accessToken);
            const encryptedRefreshToken = options.refreshToken
                ? this.encrypt(options.refreshToken)
                : undefined;
            const expiresAt = options.expiresIn
                ? new Date(Date.now() + options.expiresIn * 1000)
                : undefined;
            const tokenData = {
                userId,
                tenantId,
                service,
                accessToken: encryptedAccessToken,
                refreshToken: encryptedRefreshToken,
                expiresAt,
                scopes: options.scopes || [],
                metadata: options.metadata || {},
                createdAt: new Date(),
                updatedAt: new Date(),
            };
            const docId = `${userId}_${service}`;
            await this.firestore.collection(this.COLLECTION).doc(docId).set(tokenData);
            logger_1.logger.info('OAuth token stored', {
                userId,
                service,
                tenantId,
                expiresAt: expiresAt?.toISOString(),
            });
        }
        catch (error) {
            logger_1.logger.error('Failed to store OAuth token', { error, userId, service });
            throw error;
        }
    }
    /**
     * Get OAuth token for a user
     */
    async getToken(userId, service) {
        try {
            const docId = `${userId}_${service}`;
            const doc = await this.firestore.collection(this.COLLECTION).doc(docId).get();
            if (!doc.exists) {
                return null;
            }
            const data = doc.data();
            // Decrypt tokens
            data.accessToken = this.decrypt(data.accessToken);
            if (data.refreshToken) {
                data.refreshToken = this.decrypt(data.refreshToken);
            }
            // Check if token is expired
            if (data.expiresAt && new Date() >= data.expiresAt) {
                logger_1.logger.info('Token expired, attempting refresh', { userId, service });
                return await this.refreshTokenIfNeeded(userId, service, data);
            }
            return data;
        }
        catch (error) {
            logger_1.logger.error('Failed to get OAuth token', { error, userId, service });
            throw error;
        }
    }
    /**
     * Refresh token if expired
     */
    async refreshTokenIfNeeded(userId, service, tokenData) {
        if (!tokenData.refreshToken) {
            logger_1.logger.warn('No refresh token available', { userId, service });
            return null;
        }
        try {
            // Service-specific token refresh
            const newTokens = await this.refreshServiceToken(service, tokenData.refreshToken);
            if (newTokens) {
                // Update stored token
                await this.storeToken(userId, tokenData.tenantId, service, newTokens.accessToken, {
                    refreshToken: newTokens.refreshToken || tokenData.refreshToken,
                    expiresIn: newTokens.expiresIn,
                    scopes: tokenData.scopes,
                    metadata: tokenData.metadata,
                });
                // Return updated token data
                return await this.getToken(userId, service);
            }
            return null;
        }
        catch (error) {
            logger_1.logger.error('Token refresh failed', { error, userId, service });
            return null;
        }
    }
    /**
     * Refresh service-specific token
     */
    async refreshServiceToken(service, refreshToken) {
        switch (service) {
            case 'slack':
                return await this.refreshSlackToken(refreshToken);
            case 'gmail':
            case 'calendar':
                return await this.refreshGoogleToken(refreshToken);
            default:
                return null;
        }
    }
    /**
     * Refresh Slack token
     */
    async refreshSlackToken(refreshToken) {
        try {
            const response = await fetch('https://slack.com/api/oauth.v2.access', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    client_id: process.env.SLACK_CLIENT_ID,
                    client_secret: process.env.SLACK_CLIENT_SECRET,
                    grant_type: 'refresh_token',
                    refresh_token: refreshToken,
                }),
            });
            const data = await response.json();
            if (data.ok) {
                return {
                    accessToken: data.access_token,
                    refreshToken: data.refresh_token,
                    expiresIn: data.expires_in || 43200, // 12 hours default
                };
            }
            logger_1.logger.error('Slack token refresh failed', { error: data.error });
            return null;
        }
        catch (error) {
            logger_1.logger.error('Slack token refresh error', { error });
            return null;
        }
    }
    /**
     * Refresh Google token (Gmail/Calendar)
     */
    async refreshGoogleToken(refreshToken) {
        try {
            const response = await fetch('https://oauth2.googleapis.com/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    client_id: process.env.GMAIL_CLIENT_ID,
                    client_secret: process.env.GMAIL_CLIENT_SECRET,
                    grant_type: 'refresh_token',
                    refresh_token: refreshToken,
                }),
            });
            const data = await response.json();
            if (data.access_token) {
                return {
                    accessToken: data.access_token,
                    expiresIn: data.expires_in || 3600, // 1 hour default
                };
            }
            logger_1.logger.error('Google token refresh failed', { error: data.error });
            return null;
        }
        catch (error) {
            logger_1.logger.error('Google token refresh error', { error });
            return null;
        }
    }
    /**
     * Delete OAuth token for a user
     */
    async deleteToken(userId, service) {
        try {
            const docId = `${userId}_${service}`;
            await this.firestore.collection(this.COLLECTION).doc(docId).delete();
            logger_1.logger.info('OAuth token deleted', { userId, service });
        }
        catch (error) {
            logger_1.logger.error('Failed to delete OAuth token', { error, userId, service });
            throw error;
        }
    }
    /**
     * List all tokens for a user
     */
    async listUserTokens(userId) {
        try {
            const snapshot = await this.firestore
                .collection(this.COLLECTION)
                .where('userId', '==', userId)
                .get();
            return snapshot.docs.map((doc) => {
                const data = doc.data();
                return {
                    service: data.service,
                    expiresAt: data.expiresAt?.toDate(),
                };
            });
        }
        catch (error) {
            logger_1.logger.error('Failed to list user tokens', { error, userId });
            throw error;
        }
    }
    /**
     * Check if user has valid token for service
     */
    async hasValidToken(userId, service) {
        const token = await this.getToken(userId, service);
        return token !== null;
    }
    /**
     * Encrypt token using AES-256-GCM
     */
    encrypt(text) {
        const iv = crypto.randomBytes(16);
        const cipher = crypto.createCipheriv('aes-256-gcm', Buffer.from(this.encryptionKey, 'hex'), iv);
        let encrypted = cipher.update(text, 'utf8', 'hex');
        encrypted += cipher.final('hex');
        const authTag = cipher.getAuthTag();
        // Return: iv:authTag:encrypted
        return `${iv.toString('hex')}:${authTag.toString('hex')}:${encrypted}`;
    }
    /**
     * Decrypt token
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
     * Generate encryption key (32 bytes for AES-256)
     */
    generateEncryptionKey() {
        return crypto.randomBytes(32).toString('hex');
    }
}
exports.TokenManager = TokenManager;
// Singleton instance
exports.tokenManager = new TokenManager();
//# sourceMappingURL=tokenManager.js.map