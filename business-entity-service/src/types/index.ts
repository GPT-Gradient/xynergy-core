/**
 * Business Entity Service Types
 */

export type EntityCategory = 'continuum' | 'nexus' | 'venture' | 'enterprise';
export type EntityLifecycleState = 'concept' | 'development' | 'beta' | 'commercial' | 'graduated' | 'archived';
export type EntityStatus = 'active' | 'pending' | 'graduated' | 'archived';

/**
 * Business Entity
 */
export interface BusinessEntity {
  id: string;
  name: string;
  description: string;
  category: EntityCategory;
  lifecycleState: EntityLifecycleState;
  status: EntityStatus;

  // Continuum-specific fields
  continuumGeneration?: number;        // Gen 1, Gen 2, etc.
  continuumSlot?: number;              // 1-6 for active projects
  isActiveContinuum?: boolean;         // True if in one of 6 active slots

  // Relationships
  tenantIds: string[];                 // Associated tenant IDs
  primaryTenantId?: string;            // Main tenant for this entity

  // Metadata
  createdAt: string;
  createdBy: string;
  updatedAt: string;
  updatedBy: string;

  // Lifecycle tracking
  betaStartDate?: string;
  graduationDate?: string;

  // Feature flags
  features: {
    crm: boolean;
    slack: boolean;
    gmail: boolean;
    aso: boolean;
    marketing: boolean;
    analytics: boolean;
  };

  // Custom metadata
  metadata?: Record<string, any>;
}

/**
 * Continuum Slot Management
 */
export interface ContinuumSlot {
  slotNumber: number;                  // 1-6
  entityId: string | null;             // Null if empty
  entity: BusinessEntity | null;
  generation: number | null;
  assignedAt: string | null;
}

export interface ContinuumSlots {
  slots: ContinuumSlot[];              // 6 active slots
  pending: BusinessEntity[];           // Pending projects waiting for slots
  totalActive: number;                 // Count of filled slots
  availableSlots: number;              // Count of empty slots
}

/**
 * Graduation Request
 */
export interface GraduationRequest {
  entityId: string;
  reason?: string;
  graduatedBy: string;
  notes?: string;
}

/**
 * Onboarding Request
 */
export interface OnboardingRequest {
  entityId: string;
  targetSlot?: number;                 // Optional specific slot
  onboardedBy: string;
  notes?: string;
}

/**
 * Entity Creation Request
 */
export interface CreateEntityRequest {
  name: string;
  description: string;
  category: EntityCategory;
  continuumGeneration?: number;
  features?: Partial<BusinessEntity['features']>;
  metadata?: Record<string, any>;
  createdBy: string;
}

/**
 * Entity Update Request
 */
export interface UpdateEntityRequest {
  name?: string;
  description?: string;
  lifecycleState?: EntityLifecycleState;
  status?: EntityStatus;
  features?: Partial<BusinessEntity['features']>;
  metadata?: Record<string, any>;
  updatedBy: string;
}

/**
 * Pub/Sub Event Types
 */
export interface EntityEvent {
  eventType: 'entity.created' | 'entity.updated' | 'entity.graduated' | 'entity.onboarded' | 'entity.archived';
  entityId: string;
  entity: BusinessEntity;
  timestamp: string;
  triggeredBy: string;
  metadata?: Record<string, any>;
}
