/**
 * OAuth Provider Configurations
 */

import { OAuthProviderConfig } from '../types';

const BASE_REDIRECT_URI = process.env.BASE_REDIRECT_URI || 'https://oauth-management-service-835612502919.us-central1.run.app/api/v1/oauth/callback';

// Slack OAuth Configuration
export const SLACK_CONFIG: OAuthProviderConfig = {
  clientId: process.env.SLACK_CLIENT_ID || '',
  clientSecret: process.env.SLACK_CLIENT_SECRET || '',
  authorizationUrl: 'https://slack.com/oauth/v2/authorize',
  tokenUrl: 'https://slack.com/api/oauth.v2.access',
  scopes: [
    'channels:read',
    'channels:write',
    'chat:write',
    'users:read',
    'users:read.email',
    'files:read',
    'files:write',
    'search:read',
  ],
  redirectUri: BASE_REDIRECT_URI,
};

// Gmail (Google) OAuth Configuration
export const GMAIL_CONFIG: OAuthProviderConfig = {
  clientId: process.env.GMAIL_CLIENT_ID || process.env.GOOGLE_CLIENT_ID || '',
  clientSecret: process.env.GMAIL_CLIENT_SECRET || process.env.GOOGLE_CLIENT_SECRET || '',
  authorizationUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
  tokenUrl: 'https://oauth2.googleapis.com/token',
  scopes: [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
  ],
  redirectUri: BASE_REDIRECT_URI,
};

/**
 * Get provider configuration by name
 */
export function getProviderConfig(provider: 'slack' | 'gmail'): OAuthProviderConfig {
  switch (provider) {
    case 'slack':
      return SLACK_CONFIG;
    case 'gmail':
      return GMAIL_CONFIG;
    default:
      throw new Error(`Unknown OAuth provider: ${provider}`);
  }
}

/**
 * Validate provider configuration (ensure client ID and secret are set)
 */
export function validateProviderConfig(provider: 'slack' | 'gmail'): boolean {
  const config = getProviderConfig(provider);

  if (!config.clientId) {
    console.error(`Missing client ID for ${provider}`);
    return false;
  }

  if (!config.clientSecret) {
    console.error(`Missing client secret for ${provider}`);
    return false;
  }

  return true;
}
