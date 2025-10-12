/**
 * Phase Transition Service
 * Manages beta program phase transitions
 */

import { getFirestore } from 'firebase-admin/firestore';
import { logger } from '../utils/logger';
import { pubsubPublisher } from '../utils/pubsub';
import { emailService } from '../utils/email';
import { BetaPhase, BetaStatus, PhaseTransitionRequest } from '../types';

const PHASE_THRESHOLDS = {
  phase_1: 100,   // Phase 1 → Phase 2 at 100 users
  phase_2: 600,   // Phase 2 → Phase 3 at 600 users
};

const PHASE_ORDER: BetaPhase[] = ['phase_1', 'phase_2', 'phase_3'];

export class PhaseTransitionService {
  private get db() {
    return getFirestore();
  }

  /**
   * Check if project meets criteria for phase transition
   */
  async checkTransitionCriteria(projectId: string): Promise<{
    canTransition: boolean;
    currentPhase: BetaPhase;
    nextPhase?: BetaPhase;
    userCount: number;
    threshold?: number;
    reason: string;
  }> {
    try {
      // Get project details
      const projectDoc = await this.db.collection('business_entities').doc(projectId).get();

      if (!projectDoc.exists) {
        throw new Error('Project not found');
      }

      const projectData = projectDoc.data();
      const currentPhase: BetaPhase = projectData?.betaPhase || 'phase_1';

      // Check if already at final phase
      if (currentPhase === 'phase_3') {
        return {
          canTransition: false,
          currentPhase,
          userCount: 0,
          reason: 'Already at final phase (Phase 3)',
        };
      }

      // Get current phase index
      const currentIndex = PHASE_ORDER.indexOf(currentPhase);
      const nextPhase = PHASE_ORDER[currentIndex + 1] as BetaPhase;

      // Count beta users in current phase
      const usersQuery = await this.db
        .collection('users')
        .where('betaStatus.isBetaUser', '==', true)
        .where('betaStatus.phase', '==', currentPhase)
        .get();

      const userCount = usersQuery.size;
      const threshold = PHASE_THRESHOLDS[currentPhase];

      // Check threshold
      const canTransition = userCount >= threshold;

      return {
        canTransition,
        currentPhase,
        nextPhase,
        userCount,
        threshold,
        reason: canTransition
          ? `Ready to transition: ${userCount}/${threshold} users`
          : `Not ready: ${userCount}/${threshold} users (need ${threshold - userCount} more)`,
      };
    } catch (error) {
      logger.error('Error checking transition criteria', { error, projectId });
      throw error;
    }
  }

  /**
   * Transition project to next phase
   */
  async transitionPhase(request: PhaseTransitionRequest): Promise<{
    success: boolean;
    oldPhase: BetaPhase;
    newPhase: BetaPhase;
    usersUpdated: number;
  }> {
    try {
      // Get project
      const projectDoc = await this.db.collection('business_entities').doc(request.projectId).get();

      if (!projectDoc.exists) {
        throw new Error('Project not found');
      }

      const projectData = projectDoc.data();
      const oldPhase: BetaPhase = projectData?.betaPhase || 'phase_1';
      const newPhase = request.newPhase;

      // Validate transition
      const oldIndex = PHASE_ORDER.indexOf(oldPhase);
      const newIndex = PHASE_ORDER.indexOf(newPhase);

      if (newIndex <= oldIndex) {
        throw new Error('Can only transition to a higher phase');
      }

      if (newIndex - oldIndex > 1) {
        throw new Error('Cannot skip phases');
      }

      const now = new Date().toISOString();

      // Update project phase
      await this.db.collection('business_entities').doc(request.projectId).update({
        betaPhase: newPhase,
        phaseTransitionDate: now,
        updatedAt: now,
        updatedBy: request.triggeredBy,
      });

      // Get all beta users in the old phase
      const usersQuery = await this.db
        .collection('users')
        .where('betaStatus.isBetaUser', '==', true)
        .where('betaStatus.phase', '==', oldPhase)
        .get();

      // Update all users' phase history
      const batch = this.db.batch();

      for (const userDoc of usersQuery.docs) {
        const userData = userDoc.data();
        const betaStatus: BetaStatus = userData.betaStatus;

        // Close current phase in history
        if (betaStatus.phaseHistory.length > 0) {
          const currentPhaseRecord = betaStatus.phaseHistory[betaStatus.phaseHistory.length - 1];
          if (!currentPhaseRecord.endDate) {
            currentPhaseRecord.endDate = now;
          }
        }

        // Add new phase to history
        betaStatus.phaseHistory.push({
          phase: newPhase,
          startDate: now,
        });

        // Update current phase
        betaStatus.phase = newPhase;

        batch.update(userDoc.ref, {
          betaStatus,
          updatedAt: now,
        });

        // Send notification email if requested
        if (request.notifyUsers) {
          await emailService.sendPhaseTransitionEmail(
            userData.email,
            userData.name,
            newPhase
          );
        }
      }

      await batch.commit();

      const usersUpdated = usersQuery.size;

      logger.info('Phase transition completed', {
        projectId: request.projectId,
        oldPhase,
        newPhase,
        usersUpdated,
      });

      // Publish event
      await pubsubPublisher.publishBetaEvent({
        eventType: 'beta.phase_transition',
        phase: newPhase,
        timestamp: now,
        triggeredBy: request.triggeredBy,
        metadata: {
          projectId: request.projectId,
          oldPhase,
          newPhase,
          usersUpdated,
          reason: request.reason,
        },
      });

      return {
        success: true,
        oldPhase,
        newPhase,
        usersUpdated,
      };
    } catch (error) {
      logger.error('Error transitioning phase', { error, request });
      throw error;
    }
  }

  /**
   * Rollback phase transition (emergency use only)
   */
  async rollbackTransition(projectId: string, rolledBackBy: string): Promise<{
    success: boolean;
    message: string;
  }> {
    try {
      // Get project
      const projectDoc = await this.db.collection('business_entities').doc(projectId).get();

      if (!projectDoc.exists) {
        throw new Error('Project not found');
      }

      const projectData = projectDoc.data();
      const currentPhase: BetaPhase = projectData?.betaPhase || 'phase_1';

      // Find previous phase
      const currentIndex = PHASE_ORDER.indexOf(currentPhase);
      if (currentIndex === 0) {
        throw new Error('Cannot rollback from Phase 1');
      }

      const previousPhase = PHASE_ORDER[currentIndex - 1] as BetaPhase;
      const now = new Date().toISOString();

      // Rollback project phase
      await this.db.collection('business_entities').doc(projectId).update({
        betaPhase: previousPhase,
        phaseRollbackDate: now,
        updatedAt: now,
        updatedBy: rolledBackBy,
      });

      logger.warn('Phase transition rolled back', {
        projectId,
        from: currentPhase,
        to: previousPhase,
        rolledBackBy,
      });

      return {
        success: true,
        message: `Rolled back from ${currentPhase} to ${previousPhase}`,
      };
    } catch (error) {
      logger.error('Error rolling back transition', { error, projectId });
      throw error;
    }
  }

  /**
   * Get phase statistics
   */
  async getPhaseStats(): Promise<{
    phases: Array<{
      phase: BetaPhase;
      userCount: number;
      threshold?: number;
      percentFilled: number;
    }>;
  }> {
    try {
      const stats: Array<{
        phase: BetaPhase;
        userCount: number;
        threshold?: number;
        percentFilled: number;
      }> = [];

      for (const phase of PHASE_ORDER) {
        const usersQuery = await this.db
          .collection('users')
          .where('betaStatus.isBetaUser', '==', true)
          .where('betaStatus.phase', '==', phase)
          .get();

        const userCount = usersQuery.size;
        const threshold = PHASE_THRESHOLDS[phase as keyof typeof PHASE_THRESHOLDS];
        const percentFilled = threshold ? (userCount / threshold) * 100 : 100;

        stats.push({
          phase,
          userCount,
          threshold,
          percentFilled: Math.min(percentFilled, 100),
        });
      }

      return { phases: stats };
    } catch (error) {
      logger.error('Error getting phase stats', { error });
      throw error;
    }
  }
}
