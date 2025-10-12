/**
 * Beta Application Management Service
 */

import { getFirestore } from 'firebase-admin/firestore';
import { getAuth } from 'firebase-admin/auth';
import { v4 as uuidv4 } from 'uuid';
import { logger } from '../utils/logger';
import { pubsubPublisher } from '../utils/pubsub';
import { emailService } from '../utils/email';
import {
  BetaApplication,
  BetaStatus,
  SubmitApplicationRequest,
  ApproveApplicationRequest,
  RejectApplicationRequest,
  BatchApprovalRequest,
} from '../types';

export class ApplicationService {
  private get db() {
    return getFirestore();
  }
  private get auth() {
    return getAuth();
  }

  /**
   * Submit beta application
   */
  async submitApplication(request: SubmitApplicationRequest): Promise<BetaApplication> {
    try {
      const applicationId = uuidv4();
      const now = new Date().toISOString();

      const application: BetaApplication = {
        id: applicationId,
        email: request.email.toLowerCase(),
        name: request.name,
        company: request.company,
        role: request.role,
        linkedinUrl: request.linkedinUrl,
        twitterHandle: request.twitterHandle,
        reason: request.reason,
        experience: request.experience,
        referralSource: request.referralSource,
        status: 'pending',
        phase: request.phase || 'phase_1',
        appliedAt: now,
      };

      // Check if user already applied
      const existingQuery = await this.db
        .collection('beta_applications')
        .where('email', '==', application.email)
        .where('status', '==', 'pending')
        .get();

      if (!existingQuery.empty) {
        throw new Error('You have already submitted an application that is pending review');
      }

      await this.db.collection('beta_applications').doc(applicationId).set(application);

      logger.info('Beta application submitted', {
        applicationId,
        email: application.email,
        phase: application.phase,
      });

      // Publish event
      await pubsubPublisher.publishBetaEvent({
        eventType: 'beta.application_submitted',
        applicationId,
        phase: application.phase,
        timestamp: now,
        metadata: {
          email: application.email,
          name: application.name,
        },
      });

      return application;
    } catch (error) {
      logger.error('Error submitting application', { error, request });
      throw error;
    }
  }

  /**
   * List all applications (admin)
   */
  async listApplications(filters?: {
    status?: string;
    phase?: string;
    limit?: number;
  }): Promise<BetaApplication[]> {
    try {
      let query: any = this.db.collection('beta_applications');

      if (filters?.status) {
        query = query.where('status', '==', filters.status);
      }

      if (filters?.phase) {
        query = query.where('phase', '==', filters.phase);
      }

      query = query.orderBy('appliedAt', 'desc');

      if (filters?.limit) {
        query = query.limit(filters.limit);
      }

      const snapshot = await query.get();

      return snapshot.docs.map((doc: any) => ({
        id: doc.id,
        ...doc.data(),
      })) as BetaApplication[];
    } catch (error) {
      logger.error('Error listing applications', { error, filters });
      throw new Error('Failed to list applications');
    }
  }

  /**
   * Get application by ID
   */
  async getApplication(applicationId: string): Promise<BetaApplication | null> {
    try {
      const doc = await this.db.collection('beta_applications').doc(applicationId).get();

      if (!doc.exists) {
        return null;
      }

      return { id: doc.id, ...doc.data() } as BetaApplication;
    } catch (error) {
      logger.error('Error fetching application', { error, applicationId });
      throw new Error('Failed to fetch application');
    }
  }

  /**
   * Approve application
   */
  async approveApplication(request: ApproveApplicationRequest): Promise<{ userId: string; application: BetaApplication }> {
    try {
      const appDoc = await this.db.collection('beta_applications').doc(request.applicationId).get();

      if (!appDoc.exists) {
        throw new Error('Application not found');
      }

      const application = { id: appDoc.id, ...appDoc.data() } as BetaApplication;

      if (application.status !== 'pending') {
        throw new Error(`Application already ${application.status}`);
      }

      const now = new Date().toISOString();

      // 1. Create or get user
      let userId: string;
      try {
        const existingUser = await this.auth.getUserByEmail(application.email);
        userId = existingUser.uid;
        logger.info('Existing user found', { userId, email: application.email });
      } catch (error: any) {
        if (error.code === 'auth/user-not-found') {
          // Create new user
          const newUser = await this.auth.createUser({
            email: application.email,
            displayName: application.name,
            password: this.generateTemporaryPassword(),
          });
          userId = newUser.uid;
          logger.info('New user created', { userId, email: application.email });
        } else {
          throw error;
        }
      }

      // 2. Get all active Continuum projects for lifetime access
      const continuumQuery = await this.db
        .collection('business_entities')
        .where('category', '==', 'continuum')
        .where('isActiveContinuum', '==', true)
        .get();

      const continuumProjects = continuumQuery.docs.map(doc => doc.id);

      // 3. Determine tenant (use provided or default to NEXUS)
      const tenantId = request.tenantId || 'nexus-beta';

      // 4. Get permission template for phase
      const templateId = `beta_user_${application.phase}`;
      const templateDoc = await this.db.collection('permission_templates').doc(templateId).get();
      const permissions = request.customPermissions ||
                         (templateDoc.exists ? templateDoc.data()?.permissions : []) ||
                         ['crm.*', 'slack.read', 'gmail.read'];

      // 5. Create/Update user document with beta status
      const betaStatus: BetaStatus = {
        isBetaUser: true,
        phase: application.phase,
        joinedAt: now,
        lifetimeAccess: continuumProjects,
        phaseHistory: [{
          phase: application.phase,
          startDate: now,
        }],
        perks: ['lifetime_access', 'priority_support', 'early_features'],
      };

      const userDoc = this.db.collection('users').doc(userId);
      const userSnapshot = await userDoc.get();

      if (userSnapshot.exists) {
        // Update existing user
        await userDoc.update({
          betaStatus,
          [`tenantRoles.${tenantId}`]: {
            role: `beta_user_${application.phase}`,
            permissions,
            grantedAt: now,
            grantedBy: request.approvedBy,
          },
          activeTenantId: tenantId,
          updatedAt: now,
        });
      } else {
        // Create new user document
        await userDoc.set({
          uid: userId,
          email: application.email,
          name: application.name,
          globalRole: 'user',
          activeTenantId: tenantId,
          betaStatus,
          tenantRoles: {
            [tenantId]: {
              role: `beta_user_${application.phase}`,
              permissions,
              grantedAt: now,
              grantedBy: request.approvedBy,
            },
          },
          createdAt: now,
          updatedAt: now,
        });
      }

      // 6. Update application status
      await this.db.collection('beta_applications').doc(request.applicationId).update({
        status: 'approved',
        processedAt: now,
        processedBy: request.approvedBy,
        userId,
        tenantId,
        notes: request.notes,
      });

      const updatedApp = { ...application, status: 'approved' as const, userId, tenantId };

      logger.info('Application approved', {
        applicationId: request.applicationId,
        userId,
        email: application.email,
        phase: application.phase,
        lifetimeAccessCount: continuumProjects.length,
      });

      // 7. Send welcome email
      await emailService.sendWelcomeEmail(
        application.email,
        application.name,
        application.phase
      );

      // 8. Publish event
      await pubsubPublisher.publishBetaEvent({
        eventType: 'beta.user_approved',
        applicationId: request.applicationId,
        userId,
        phase: application.phase,
        timestamp: now,
        triggeredBy: request.approvedBy,
        metadata: {
          email: application.email,
          tenantId,
          lifetimeAccessCount: continuumProjects.length,
        },
      });

      return { userId, application: updatedApp };
    } catch (error) {
      logger.error('Error approving application', { error, request });
      throw error;
    }
  }

  /**
   * Reject application
   */
  async rejectApplication(request: RejectApplicationRequest): Promise<BetaApplication> {
    try {
      const appDoc = await this.db.collection('beta_applications').doc(request.applicationId).get();

      if (!appDoc.exists) {
        throw new Error('Application not found');
      }

      const application = { id: appDoc.id, ...appDoc.data() } as BetaApplication;

      if (application.status !== 'pending') {
        throw new Error(`Application already ${application.status}`);
      }

      const now = new Date().toISOString();

      await this.db.collection('beta_applications').doc(request.applicationId).update({
        status: 'rejected',
        processedAt: now,
        processedBy: request.rejectedBy,
        rejectionReason: request.reason,
        notes: request.notes,
      });

      logger.info('Application rejected', {
        applicationId: request.applicationId,
        email: application.email,
      });

      // Send rejection email
      await emailService.sendRejectionEmail(
        application.email,
        application.name,
        request.reason
      );

      // Publish event
      await pubsubPublisher.publishBetaEvent({
        eventType: 'beta.user_rejected',
        applicationId: request.applicationId,
        timestamp: now,
        triggeredBy: request.rejectedBy,
      });

      return { ...application, status: 'rejected' };
    } catch (error) {
      logger.error('Error rejecting application', { error, request });
      throw error;
    }
  }

  /**
   * Move application to waitlist
   */
  async waitlistApplication(applicationId: string, processedBy: string): Promise<BetaApplication> {
    try {
      const appDoc = await this.db.collection('beta_applications').doc(applicationId).get();

      if (!appDoc.exists) {
        throw new Error('Application not found');
      }

      const application = { id: appDoc.id, ...appDoc.data() } as BetaApplication;

      if (application.status !== 'pending') {
        throw new Error(`Application already ${application.status}`);
      }

      const now = new Date().toISOString();

      await this.db.collection('beta_applications').doc(applicationId).update({
        status: 'waitlist',
        processedAt: now,
        processedBy,
      });

      logger.info('Application moved to waitlist', {
        applicationId,
        email: application.email,
      });

      // Send waitlist email
      await emailService.sendWaitlistEmail(application.email, application.name);

      // Publish event
      await pubsubPublisher.publishBetaEvent({
        eventType: 'beta.user_waitlisted',
        applicationId,
        timestamp: now,
        triggeredBy: processedBy,
      });

      return { ...application, status: 'waitlist' };
    } catch (error) {
      logger.error('Error waitlisting application', { error, applicationId });
      throw error;
    }
  }

  /**
   * Batch approve applications
   */
  async batchApprove(request: BatchApprovalRequest): Promise<{ successful: string[]; failed: { id: string; error: string }[] }> {
    const successful: string[] = [];
    const failed: { id: string; error: string }[] = [];

    for (const applicationId of request.applicationIds) {
      try {
        await this.approveApplication({
          applicationId,
          approvedBy: request.approvedBy,
          tenantId: request.tenantId,
        });
        successful.push(applicationId);
      } catch (error: any) {
        failed.push({
          id: applicationId,
          error: error.message || 'Unknown error',
        });
      }
    }

    logger.info('Batch approval completed', {
      total: request.applicationIds.length,
      successful: successful.length,
      failed: failed.length,
    });

    return { successful, failed };
  }

  /**
   * Generate temporary password
   */
  private generateTemporaryPassword(): string {
    const length = 16;
    const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
    let password = '';
    for (let i = 0; i < length; i++) {
      password += charset.charAt(Math.floor(Math.random() * charset.length));
    }
    return password;
  }
}
