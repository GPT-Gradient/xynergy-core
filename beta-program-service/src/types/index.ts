/**
 * Beta Program Service Types
 */

export type ApplicationStatus = 'pending' | 'approved' | 'rejected' | 'waitlist';
export type BetaPhase = 'phase_1' | 'phase_2' | 'phase_3';

/**
 * Beta Application
 */
export interface BetaApplication {
  id: string;
  email: string;
  name: string;
  company?: string;
  role?: string;
  linkedinUrl?: string;
  twitterHandle?: string;
  reason: string;
  experience?: string;
  referralSource?: string;

  // Application metadata
  status: ApplicationStatus;
  phase: BetaPhase;                    // Which phase they're applying for
  appliedAt: string;
  processedAt?: string;
  processedBy?: string;

  // Approval/Rejection details
  rejectionReason?: string;
  notes?: string;

  // User creation
  userId?: string;                     // Created after approval
  tenantId?: string;                   // Assigned tenant
}

/**
 * Beta User Status
 */
export interface BetaStatus {
  isBetaUser: boolean;
  phase: BetaPhase;                    // Phase they joined
  joinedAt: string;
  joinedThroughProject?: string;       // Which project they joined through

  // Lifetime access
  lifetimeAccess: string[];            // Array of project/entity IDs

  // Phase history
  phaseHistory: {
    phase: BetaPhase;
    startDate: string;
    endDate?: string;
  }[];

  // Perks and benefits
  perks: string[];                     // e.g., ['lifetime_access', 'priority_support', 'early_features']
}

/**
 * Application Submission Request
 */
export interface SubmitApplicationRequest {
  email: string;
  name: string;
  company?: string;
  role?: string;
  linkedinUrl?: string;
  twitterHandle?: string;
  reason: string;
  experience?: string;
  referralSource?: string;
  phase?: BetaPhase;                   // Defaults to phase_1
}

/**
 * Application Approval Request
 */
export interface ApproveApplicationRequest {
  applicationId: string;
  approvedBy: string;
  tenantId?: string;                   // Optional specific tenant
  notes?: string;
  customPermissions?: string[];        // Override default permissions
}

/**
 * Application Rejection Request
 */
export interface RejectApplicationRequest {
  applicationId: string;
  rejectedBy: string;
  reason?: string;
  notes?: string;
}

/**
 * Batch Approval Request
 */
export interface BatchApprovalRequest {
  applicationIds: string[];
  approvedBy: string;
  tenantId?: string;
}

/**
 * Phase Transition Request
 */
export interface PhaseTransitionRequest {
  projectId: string;
  newPhase: BetaPhase;
  triggeredBy: string;
  reason?: string;
  notifyUsers?: boolean;               // Send email notification
}

/**
 * Lifetime Access Grant Request
 */
export interface GrantLifetimeAccessRequest {
  projectId: string;
  grantedBy: string;
  notifyUsers?: boolean;
}

/**
 * Pub/Sub Event Types
 */
export interface BetaEvent {
  eventType: 'beta.application_submitted' | 'beta.user_approved' | 'beta.user_rejected' |
             'beta.phase_transition' | 'beta.access_granted' | 'beta.user_waitlisted';
  applicationId?: string;
  userId?: string;
  phase?: BetaPhase;
  timestamp: string;
  triggeredBy?: string;
  metadata?: Record<string, any>;
}

/**
 * Email Templates
 */
export interface EmailTemplate {
  to: string;
  subject: string;
  text: string;
  html?: string;
}
