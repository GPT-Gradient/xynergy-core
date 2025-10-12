/**
 * Lifetime Access Management Service
 * Manages beta users' lifetime access to Continuum projects
 */

import { getFirestore } from 'firebase-admin/firestore';
import { logger } from '../utils/logger';
import { pubsubPublisher } from '../utils/pubsub';
import { emailService } from '../utils/email';
import { BetaStatus, GrantLifetimeAccessRequest } from '../types';

export class LifetimeAccessService {
  private get db() {
    return getFirestore();
  }

  /**
   * Grant lifetime access to new project for all beta users
   */
  async grantAccessToAllBetaUsers(request: GrantLifetimeAccessRequest): Promise<{ usersUpdated: number }> {
    try {
      // Get the project details
      const projectDoc = await this.db.collection('business_entities').doc(request.projectId).get();

      if (!projectDoc.exists) {
        throw new Error('Project not found');
      }

      const project = projectDoc.data();
      const projectName = project?.name || 'New Project';

      // Get all beta users
      const usersQuery = await this.db
        .collection('users')
        .where('betaStatus.isBetaUser', '==', true)
        .get();

      const batch = this.db.batch();
      let updateCount = 0;

      for (const userDoc of usersQuery.docs) {
        const userData = userDoc.data();
        const betaStatus: BetaStatus = userData.betaStatus;

        // Add project to lifetime access if not already there
        if (!betaStatus.lifetimeAccess.includes(request.projectId)) {
          betaStatus.lifetimeAccess.push(request.projectId);

          batch.update(userDoc.ref, {
            betaStatus,
            updatedAt: new Date().toISOString(),
          });

          updateCount++;

          // Send notification email if requested
          if (request.notifyUsers) {
            await emailService.sendNewProjectAccessEmail(
              userData.email,
              userData.name,
              projectName
            );
          }
        }
      }

      if (updateCount > 0) {
        await batch.commit();
      }

      logger.info('Lifetime access granted to all beta users', {
        projectId: request.projectId,
        projectName,
        usersUpdated: updateCount,
      });

      // Publish event
      await pubsubPublisher.publishBetaEvent({
        eventType: 'beta.access_granted',
        timestamp: new Date().toISOString(),
        triggeredBy: request.grantedBy,
        metadata: {
          projectId: request.projectId,
          projectName,
          usersUpdated: updateCount,
        },
      });

      return { usersUpdated: updateCount };
    } catch (error) {
      logger.error('Error granting lifetime access', { error, request });
      throw error;
    }
  }

  /**
   * Get user's beta benefits
   */
  async getUserBenefits(userId: string): Promise<{
    isBetaUser: boolean;
    phase?: string;
    joinedAt?: string;
    lifetimeAccessCount: number;
    projects: Array<{ id: string; name: string; status: string }>;
    perks: string[];
  }> {
    try {
      const userDoc = await this.db.collection('users').doc(userId).get();

      if (!userDoc.exists) {
        throw new Error('User not found');
      }

      const userData = userDoc.data();
      const betaStatus: BetaStatus | undefined = userData?.betaStatus;

      if (!betaStatus || !betaStatus.isBetaUser) {
        return {
          isBetaUser: false,
          lifetimeAccessCount: 0,
          projects: [],
          perks: [],
        };
      }

      // Get project details
      const projects = [];
      for (const projectId of betaStatus.lifetimeAccess) {
        const projectDoc = await this.db.collection('business_entities').doc(projectId).get();
        if (projectDoc.exists) {
          const projectData = projectDoc.data();
          projects.push({
            id: projectId,
            name: projectData?.name || 'Unknown',
            status: projectData?.status || 'unknown',
          });
        }
      }

      return {
        isBetaUser: true,
        phase: betaStatus.phase,
        joinedAt: betaStatus.joinedAt,
        lifetimeAccessCount: betaStatus.lifetimeAccess.length,
        projects,
        perks: betaStatus.perks || [],
      };
    } catch (error) {
      logger.error('Error getting user benefits', { error, userId });
      throw error;
    }
  }

  /**
   * Get all projects user has access to
   */
  async getUserProjects(userId: string): Promise<Array<{ id: string; name: string; category: string; status: string }>> {
    try {
      const userDoc = await this.db.collection('users').doc(userId).get();

      if (!userDoc.exists) {
        throw new Error('User not found');
      }

      const userData = userDoc.data();
      const betaStatus: BetaStatus | undefined = userData?.betaStatus;

      if (!betaStatus || !betaStatus.isBetaUser) {
        return [];
      }

      const projects = [];
      for (const projectId of betaStatus.lifetimeAccess) {
        const projectDoc = await this.db.collection('business_entities').doc(projectId).get();
        if (projectDoc.exists) {
          const projectData = projectDoc.data();
          projects.push({
            id: projectId,
            name: projectData?.name || 'Unknown',
            category: projectData?.category || 'unknown',
            status: projectData?.status || 'unknown',
          });
        }
      }

      return projects;
    } catch (error) {
      logger.error('Error getting user projects', { error, userId });
      throw error;
    }
  }

  /**
   * Get all beta users count by phase
   */
  async getBetaUserStats(): Promise<{
    total: number;
    byPhase: Record<string, number>;
    totalLifetimeAccess: number;
  }> {
    try {
      const usersQuery = await this.db
        .collection('users')
        .where('betaStatus.isBetaUser', '==', true)
        .get();

      const byPhase: Record<string, number> = {};
      let totalLifetimeAccess = 0;

      usersQuery.docs.forEach(doc => {
        const userData = doc.data();
        const betaStatus: BetaStatus = userData.betaStatus;

        // Count by phase
        const phase = betaStatus.phase;
        byPhase[phase] = (byPhase[phase] || 0) + 1;

        // Count total lifetime access grants
        totalLifetimeAccess += betaStatus.lifetimeAccess.length;
      });

      return {
        total: usersQuery.size,
        byPhase,
        totalLifetimeAccess,
      };
    } catch (error) {
      logger.error('Error getting beta user stats', { error });
      throw error;
    }
  }
}
