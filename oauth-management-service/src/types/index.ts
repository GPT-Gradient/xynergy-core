/**
 * Type definitions for OAuth Management Service
 */

// OAuth Providers
export type OAuthProvider = 'slack' | 'gmail';

// OAuth Connection Status
export type ConnectionStatus = 'active' | 'expired' | 'revoked' | 'error';

// OAuth Connection (stored in Firestore)
export interface OAuthConnection {
  id: string;
  userId: string;
  tenantId: string;
  provider: OAuthProvider;

  // Provider-specific identifiers
  providerUserId: string;  // Slack user ID or Gmail email
  providerTeamId?: string; // Slack workspace ID (for multi-workspace support)
  email: string;

  // Token data (encrypted)
  encryptedAccessToken: string;
  encryptedRefreshToken?: string;
  tokenType: string;
  expiresAt: string;

  // Scopes granted
  scopes: string[];

  // Connection metadata
  status: ConnectionStatus;
  createdAt: string;
  updatedAt: string;
  lastRefreshedAt?: string;
  lastHealthCheckAt?: string;
  healthCheckStatus?: 'healthy' | 'unhealthy';
  healthCheckError?: string;

  // Revocation
  revokedAt?: string;
  revokedBy?: string;
  revokedReason?: string;
}

// OAuth State Parameter (stored in Redis with 15 min TTL)
export interface OAuthState {
  userId: string;
  tenantId: string;
  provider: OAuthProvider;
  redirectUri: string;
  createdAt: string;
  expiresAt: string;
}

// OAuth Provider Configuration
export interface OAuthProviderConfig {
  clientId: string;
  clientSecret: string;
  authorizationUrl: string;
  tokenUrl: string;
  scopes: string[];
  redirectUri: string;
}

// OAuth URL Generation Request
export interface GenerateOAuthUrlRequest {
  userId: string;
  tenantId: string;
  provider: OAuthProvider;
  redirectUri?: string; // Optional custom redirect URI
}

// OAuth URL Generation Response
export interface GenerateOAuthUrlResponse {
  authorizationUrl: string;
  state: string;
  expiresAt: string;
}

// OAuth Callback Request
export interface OAuthCallbackRequest {
  code: string;
  state: string;
}

// OAuth Callback Response
export interface OAuthCallbackResponse {
  success: boolean;
  connectionId: string;
  provider: OAuthProvider;
  email: string;
}

// Token Exchange Response (from OAuth provider)
export interface TokenExchangeResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in: number;
  scope?: string;

  // Provider-specific fields
  team?: { id: string; name: string }; // Slack
  authed_user?: { id: string; email: string }; // Slack
  user?: { email: string }; // Gmail
}

// Get Token Request (internal API for services)
export interface GetTokenRequest {
  userId: string;
  tenantId: string;
  provider: OAuthProvider;
  teamId?: string; // Optional for Slack multi-workspace
}

// Get Token Response
export interface GetTokenResponse {
  accessToken: string;
  tokenType: string;
  expiresAt: string;
  scopes: string[];
}

// Health Check Result
export interface HealthCheckResult {
  connectionId: string;
  provider: OAuthProvider;
  status: 'healthy' | 'unhealthy';
  checkedAt: string;
  error?: string;
  responseTime?: number;
}

// Token Refresh Job Result
export interface TokenRefreshResult {
  connectionId: string;
  provider: OAuthProvider;
  success: boolean;
  error?: string;
  newExpiresAt?: string;
}

// Admin Dashboard Stats
export interface OAuthStats {
  totalConnections: number;
  activeConnections: number;
  expiredConnections: number;
  revokedConnections: number;
  errorConnections: number;

  byProvider: {
    [key in OAuthProvider]: {
      total: number;
      active: number;
      expired: number;
    };
  };

  recentHealthChecks: HealthCheckResult[];
  recentRefreshes: TokenRefreshResult[];
}

// Connection List Query
export interface ListConnectionsQuery {
  userId?: string;
  tenantId?: string;
  provider?: OAuthProvider;
  status?: ConnectionStatus;
  limit?: number;
}
