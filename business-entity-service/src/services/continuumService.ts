/**
 * Continuum Slot Management Service
 * Manages the 6 active Continuum project slots and lifecycle
 */

import { getFirestore } from 'firebase-admin/firestore';
import { v4 as uuidv4 } from 'uuid';
import { logger } from '../utils/logger';
import { pubsubPublisher } from '../utils/pubsub';
import {
  BusinessEntity,
  ContinuumSlot,
  ContinuumSlots,
  GraduationRequest,
  OnboardingRequest,
  CreateEntityRequest,
} from '../types';

const MAX_CONTINUUM_SLOTS = 6;

export class ContinuumService {
  private get db() {
    return getFirestore();
  }

  /**
   * Get current state of all 6 Continuum slots
   */
  async getSlots(): Promise<ContinuumSlots> {
    try {
      // Get all active Continuum projects
      const activeQuery = await this.db
        .collection('business_entities')
        .where('category', '==', 'continuum')
        .where('isActiveContinuum', '==', true)
        .orderBy('continuumSlot')
        .get();

      // Get pending Continuum projects
      const pendingQuery = await this.db
        .collection('business_entities')
        .where('category', '==', 'continuum')
        .where('status', '==', 'pending')
        .orderBy('createdAt')
        .get();

      const activeEntities: BusinessEntity[] = activeQuery.docs.map(doc => ({ id: doc.id, ...doc.data() } as BusinessEntity));
      const pendingEntities: BusinessEntity[] = pendingQuery.docs.map(doc => ({ id: doc.id, ...doc.data() } as BusinessEntity));

      // Build 6-slot array
      const slots: ContinuumSlot[] = [];
      for (let i = 1; i <= MAX_CONTINUUM_SLOTS; i++) {
        const entity = activeEntities.find(e => e.continuumSlot === i);
        slots.push({
          slotNumber: i,
          entityId: entity?.id || null,
          entity: entity || null,
          generation: entity?.continuumGeneration || null,
          assignedAt: entity?.betaStartDate || null,
        });
      }

      return {
        slots,
        pending: pendingEntities,
        totalActive: activeEntities.length,
        availableSlots: MAX_CONTINUUM_SLOTS - activeEntities.length,
      };
    } catch (error) {
      logger.error('Error fetching Continuum slots', { error });
      throw new Error('Failed to fetch Continuum slots');
    }
  }

  /**
   * Create new Continuum project
   */
  async createContinuumProject(request: CreateEntityRequest): Promise<BusinessEntity> {
    try {
      const entityId = uuidv4();
      const now = new Date().toISOString();

      // Check if we have available slots
      const currentSlots = await this.getSlots();
      const hasAvailableSlot = currentSlots.availableSlots > 0;

      const entity: BusinessEntity = {
        id: entityId,
        name: request.name,
        description: request.description,
        category: 'continuum',
        lifecycleState: hasAvailableSlot ? 'beta' : 'concept',
        status: hasAvailableSlot ? 'active' : 'pending',
        continuumGeneration: request.continuumGeneration || 1,
        isActiveContinuum: false,
        tenantIds: [],
        features: {
          crm: request.features?.crm ?? true,
          slack: request.features?.slack ?? true,
          gmail: request.features?.gmail ?? true,
          aso: request.features?.aso ?? true,
          marketing: request.features?.marketing ?? true,
          analytics: request.features?.analytics ?? true,
        },
        metadata: request.metadata || {},
        createdAt: now,
        createdBy: request.createdBy,
        updatedAt: now,
        updatedBy: request.createdBy,
      };

      await this.db.collection('business_entities').doc(entityId).set(entity);

      logger.info('Continuum project created', {
        entityId,
        name: entity.name,
        status: entity.status,
        hasAvailableSlot,
      });

      // Publish event
      await pubsubPublisher.publishEntityEvent({
        eventType: 'entity.created',
        entityId,
        entity,
        timestamp: now,
        triggeredBy: request.createdBy,
      });

      return entity;
    } catch (error) {
      logger.error('Error creating Continuum project', { error, request });
      throw new Error('Failed to create Continuum project');
    }
  }

  /**
   * Graduate a Continuum project (free up slot)
   */
  async graduateProject(request: GraduationRequest): Promise<BusinessEntity> {
    try {
      const entityRef = this.db.collection('business_entities').doc(request.entityId);
      const entityDoc = await entityRef.get();

      if (!entityDoc.exists) {
        throw new Error('Entity not found');
      }

      const entity = { id: entityDoc.id, ...entityDoc.data() } as BusinessEntity;

      if (entity.category !== 'continuum') {
        throw new Error('Only Continuum projects can be graduated');
      }

      if (entity.status === 'graduated') {
        throw new Error('Project already graduated');
      }

      const now = new Date().toISOString();
      const freedSlot = entity.continuumSlot;

      // Update entity
      const updates: Partial<BusinessEntity> = {
        lifecycleState: 'commercial',
        status: 'graduated',
        graduationDate: now,
        isActiveContinuum: false,
        continuumSlot: undefined, // Free the slot
        updatedAt: now,
        updatedBy: request.graduatedBy,
      };

      await entityRef.update(updates);

      const updatedEntity = { ...entity, ...updates };

      logger.info('Project graduated', {
        entityId: request.entityId,
        name: entity.name,
        freedSlot,
        graduatedBy: request.graduatedBy,
      });

      // Publish event
      await pubsubPublisher.publishEntityEvent({
        eventType: 'entity.graduated',
        entityId: request.entityId,
        entity: updatedEntity,
        timestamp: now,
        triggeredBy: request.graduatedBy,
        metadata: {
          reason: request.reason,
          notes: request.notes,
          freedSlot,
        },
      });

      return updatedEntity;
    } catch (error) {
      logger.error('Error graduating project', { error, request });
      throw error;
    }
  }

  /**
   * Onboard a pending project to an active slot
   */
  async onboardProject(request: OnboardingRequest): Promise<BusinessEntity> {
    try {
      const currentSlots = await this.getSlots();

      if (currentSlots.availableSlots === 0) {
        throw new Error('No available Continuum slots. Graduate a project first.');
      }

      const entityRef = this.db.collection('business_entities').doc(request.entityId);
      const entityDoc = await entityRef.get();

      if (!entityDoc.exists) {
        throw new Error('Entity not found');
      }

      const entity = { id: entityDoc.id, ...entityDoc.data() } as BusinessEntity;

      if (entity.category !== 'continuum') {
        throw new Error('Only Continuum projects can be onboarded');
      }

      if (entity.status !== 'pending') {
        throw new Error('Only pending projects can be onboarded');
      }

      // Find first available slot or use requested slot
      let targetSlot: number;
      if (request.targetSlot && request.targetSlot >= 1 && request.targetSlot <= MAX_CONTINUUM_SLOTS) {
        const slot = currentSlots.slots[request.targetSlot - 1];
        if (slot.entityId !== null) {
          throw new Error(`Slot ${request.targetSlot} is already occupied`);
        }
        targetSlot = request.targetSlot;
      } else {
        const emptySlot = currentSlots.slots.find(s => s.entityId === null);
        if (!emptySlot) {
          throw new Error('No available slots found');
        }
        targetSlot = emptySlot.slotNumber;
      }

      const now = new Date().toISOString();

      // Create associated tenant
      const tenantId = `${entity.name.toLowerCase().replace(/\s+/g, '-')}-continuum`;
      const tenant = {
        id: tenantId,
        name: `${entity.name} (Continuum)`,
        type: 'continuum',
        businessEntityId: entity.id,
        status: 'active',
        createdAt: now,
        updatedAt: now,
        features: entity.features,
      };

      await this.db.collection('tenants').doc(tenantId).set(tenant);

      // Update entity
      const updates: Partial<BusinessEntity> = {
        status: 'active',
        lifecycleState: 'beta',
        isActiveContinuum: true,
        continuumSlot: targetSlot,
        betaStartDate: now,
        tenantIds: [tenantId],
        primaryTenantId: tenantId,
        updatedAt: now,
        updatedBy: request.onboardedBy,
      };

      await entityRef.update(updates);

      const updatedEntity = { ...entity, ...updates };

      logger.info('Project onboarded', {
        entityId: request.entityId,
        name: entity.name,
        slot: targetSlot,
        tenantId,
        onboardedBy: request.onboardedBy,
      });

      // Publish event
      await pubsubPublisher.publishEntityEvent({
        eventType: 'entity.onboarded',
        entityId: request.entityId,
        entity: updatedEntity,
        timestamp: now,
        triggeredBy: request.onboardedBy,
        metadata: {
          slot: targetSlot,
          tenantId,
          notes: request.notes,
        },
      });

      return updatedEntity;
    } catch (error) {
      logger.error('Error onboarding project', { error, request });
      throw error;
    }
  }

  /**
   * Get all Continuum projects by generation
   */
  async getByGeneration(generation: number): Promise<BusinessEntity[]> {
    try {
      const query = await this.db
        .collection('business_entities')
        .where('category', '==', 'continuum')
        .where('continuumGeneration', '==', generation)
        .orderBy('createdAt', 'desc')
        .get();

      return query.docs.map(doc => ({ id: doc.id, ...doc.data() } as BusinessEntity));
    } catch (error) {
      logger.error('Error fetching projects by generation', { error, generation });
      throw new Error('Failed to fetch projects by generation');
    }
  }

  /**
   * Get all generations summary
   */
  async getGenerations(): Promise<{ generation: number; activeCount: number; totalCount: number; graduatedCount: number }[]> {
    try {
      const query = await this.db
        .collection('business_entities')
        .where('category', '==', 'continuum')
        .get();

      const projects = query.docs.map(doc => doc.data() as BusinessEntity);
      const generationMap = new Map<number, { active: number; total: number; graduated: number }>();

      projects.forEach(project => {
        const gen = project.continuumGeneration || 1;
        const existing = generationMap.get(gen) || { active: 0, total: 0, graduated: 0 };

        existing.total++;
        if (project.status === 'active') existing.active++;
        if (project.status === 'graduated') existing.graduated++;

        generationMap.set(gen, existing);
      });

      return Array.from(generationMap.entries())
        .map(([generation, counts]) => ({
          generation,
          activeCount: counts.active,
          totalCount: counts.total,
          graduatedCount: counts.graduated,
        }))
        .sort((a, b) => a.generation - b.generation);
    } catch (error) {
      logger.error('Error fetching generations', { error });
      throw new Error('Failed to fetch generations');
    }
  }
}
