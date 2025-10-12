/**
 * Health Monitoring Service
 * Tests OAuth connections and monitors health
 */

import axios from 'axios';
import { WebClient } from '@slack/web-api';
import { google } from 'googleapis';
import { getFirestore } from 'firebase-admin/firestore';
import { logger } from '../utils/logger';
import { kmsService } from '../utils/kms';
import { OAuthConnection, HealthCheckResult } from '../types';

export class HealthService {
  private get db() {
    return getFirestore();
  }

  /**
   * Check health of a single connection
   */
  async checkConnectionHealth(connectionId: string): Promise<HealthCheckResult> {
    const startTime = Date.now();

    try {
      // Get connection
      const connectionDoc = await this.db.collection('oauth_connections').doc(connectionId).get();

      if (!connectionDoc.exists) {
        throw new Error('Connection not found');
      }

      const connection = connectionDoc.data() as OAuthConnection;

      // Check if token expired
      const now = new Date();
      const expiresAt = new Date(connection.expiresAt);

      if (expiresAt <= now) {
        const result: HealthCheckResult = {
          connectionId,
          provider: connection.provider,
          status: 'unhealthy',
          checkedAt: now.toISOString(),
          error: 'Token expired',
        };

        await this.updateHealthStatus(connectionId, result);
        return result;
      }

      // Decrypt access token
      const accessToken = await kmsService.decryptToken(connection.encryptedAccessToken);

      // Test connection based on provider
      let isHealthy = false;
      let error: string | undefined;

      if (connection.provider === 'slack') {
        const testResult = await this.testSlackConnection(accessToken);
        isHealthy = testResult.success;
        error = testResult.error;
      } else if (connection.provider === 'gmail') {
        const testResult = await this.testGmailConnection(accessToken);
        isHealthy = testResult.success;
        error = testResult.error;
      }

      const responseTime = Date.now() - startTime;

      const result: HealthCheckResult = {
        connectionId,
        provider: connection.provider,
        status: isHealthy ? 'healthy' : 'unhealthy',
        checkedAt: new Date().toISOString(),
        error,
        responseTime,
      };

      await this.updateHealthStatus(connectionId, result);

      logger.info('Connection health check completed', {
        connectionId,
        provider: connection.provider,
        status: result.status,
        responseTime,
      });

      return result;
    } catch (error: any) {
      const result: HealthCheckResult = {
        connectionId,
        provider: 'slack', // Default
        status: 'unhealthy',
        checkedAt: new Date().toISOString(),
        error: error.message,
        responseTime: Date.now() - startTime,
      };

      logger.error('Connection health check failed', { error, connectionId });
      return result;
    }
  }

  /**
   * Check health of all active connections
   */
  async checkAllConnections(): Promise<HealthCheckResult[]> {
    try {
      const activeQuery = await this.db
        .collection('oauth_connections')
        .where('status', '==', 'active')
        .get();

      logger.info('Starting health check for all connections', { count: activeQuery.size });

      const results: HealthCheckResult[] = [];

      for (const doc of activeQuery.docs) {
        const result = await this.checkConnectionHealth(doc.id);
        results.push(result);
      }

      const healthyCount = results.filter(r => r.status === 'healthy').length;
      logger.info('Health check batch completed', {
        total: results.length,
        healthy: healthyCount,
        unhealthy: results.length - healthyCount,
      });

      return results;
    } catch (error) {
      logger.error('Error checking all connections', { error });
      throw error;
    }
  }

  /**
   * Test Slack connection
   */
  private async testSlackConnection(accessToken: string): Promise<{ success: boolean; error?: string }> {
    try {
      const client = new WebClient(accessToken);
      await client.auth.test();
      return { success: true };
    } catch (error: any) {
      logger.error('Slack health check failed', { error: error.message });
      return { success: false, error: error.message };
    }
  }

  /**
   * Test Gmail connection
   */
  private async testGmailConnection(accessToken: string): Promise<{ success: boolean; error?: string }> {
    try {
      const oauth2Client = new google.auth.OAuth2();
      oauth2Client.setCredentials({ access_token: accessToken });

      const gmail = google.gmail({ version: 'v1', auth: oauth2Client });
      await gmail.users.getProfile({ userId: 'me' });

      return { success: true };
    } catch (error: any) {
      logger.error('Gmail health check failed', { error: error.message });
      return { success: false, error: error.message };
    }
  }

  /**
   * Update health status in Firestore
   */
  private async updateHealthStatus(connectionId: string, result: HealthCheckResult): Promise<void> {
    try {
      const now = new Date().toISOString();

      await this.db.collection('oauth_connections').doc(connectionId).update({
        lastHealthCheckAt: result.checkedAt,
        healthCheckStatus: result.status,
        healthCheckError: result.error || null,
        updatedAt: now,
      });
    } catch (error) {
      logger.error('Error updating health status', { error, connectionId });
      // Don't throw - health check completed, just update failed
    }
  }

  /**
   * Get health statistics
   */
  async getHealthStats(): Promise<{
    totalConnections: number;
    healthy: number;
    unhealthy: number;
    notChecked: number;
    byProvider: {
      slack: { total: number; healthy: number; unhealthy: number };
      gmail: { total: number; healthy: number; unhealthy: number };
    };
  }> {
    try {
      const allConnections = await this.db
        .collection('oauth_connections')
        .where('status', '==', 'active')
        .get();

      const stats = {
        totalConnections: allConnections.size,
        healthy: 0,
        unhealthy: 0,
        notChecked: 0,
        byProvider: {
          slack: { total: 0, healthy: 0, unhealthy: 0 },
          gmail: { total: 0, healthy: 0, unhealthy: 0 },
        },
      };

      for (const doc of allConnections.docs) {
        const connection = doc.data() as OAuthConnection;

        // Count by provider
        if (connection.provider === 'slack') {
          stats.byProvider.slack.total++;
        } else if (connection.provider === 'gmail') {
          stats.byProvider.gmail.total++;
        }

        // Count by health status
        if (!connection.lastHealthCheckAt) {
          stats.notChecked++;
        } else if (connection.healthCheckStatus === 'healthy') {
          stats.healthy++;
          if (connection.provider === 'slack') {
            stats.byProvider.slack.healthy++;
          } else if (connection.provider === 'gmail') {
            stats.byProvider.gmail.healthy++;
          }
        } else {
          stats.unhealthy++;
          if (connection.provider === 'slack') {
            stats.byProvider.slack.unhealthy++;
          } else if (connection.provider === 'gmail') {
            stats.byProvider.gmail.unhealthy++;
          }
        }
      }

      return stats;
    } catch (error) {
      logger.error('Error getting health stats', { error });
      throw error;
    }
  }
}
