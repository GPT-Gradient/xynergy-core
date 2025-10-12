/**
 * General Entity Management Service
 * CRUD operations for all business entities
 */

import { getFirestore } from 'firebase-admin/firestore';
import { v4 as uuidv4 } from 'uuid';
import { logger } from '../utils/logger';
import { pubsubPublisher } from '../utils/pubsub';
import {
  BusinessEntity,
  CreateEntityRequest,
  UpdateEntityRequest,
} from '../types';

export class EntityService {
  private get db() {
    return getFirestore();
  }

  /**
   * Create new business entity
   */
  async createEntity(request: CreateEntityRequest): Promise<BusinessEntity> {
    try {
      const entityId = uuidv4();
      const now = new Date().toISOString();

      const entity: BusinessEntity = {
        id: entityId,
        name: request.name,
        description: request.description,
        category: request.category,
        lifecycleState: 'concept',
        status: 'pending',
        tenantIds: [],
        features: {
          crm: request.features?.crm ?? true,
          slack: request.features?.slack ?? false,
          gmail: request.features?.gmail ?? false,
          aso: request.features?.aso ?? false,
          marketing: request.features?.marketing ?? false,
          analytics: request.features?.analytics ?? true,
        },
        metadata: request.metadata || {},
        createdAt: now,
        createdBy: request.createdBy,
        updatedAt: now,
        updatedBy: request.createdBy,
      };

      // Add category-specific fields
      if (request.category === 'continuum' && request.continuumGeneration) {
        entity.continuumGeneration = request.continuumGeneration;
        entity.isActiveContinuum = false;
      }

      await this.db.collection('business_entities').doc(entityId).set(entity);

      logger.info('Entity created', {
        entityId,
        name: entity.name,
        category: entity.category,
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
      logger.error('Error creating entity', { error, request });
      throw new Error('Failed to create entity');
    }
  }

  /**
   * Get entity by ID
   */
  async getEntity(entityId: string): Promise<BusinessEntity | null> {
    try {
      const doc = await this.db.collection('business_entities').doc(entityId).get();

      if (!doc.exists) {
        return null;
      }

      return { id: doc.id, ...doc.data() } as BusinessEntity;
    } catch (error) {
      logger.error('Error fetching entity', { error, entityId });
      throw new Error('Failed to fetch entity');
    }
  }

  /**
   * List all entities (with optional filters)
   */
  async listEntities(filters?: {
    category?: string;
    status?: string;
    lifecycleState?: string;
    limit?: number;
  }): Promise<BusinessEntity[]> {
    try {
      let query: any = this.db.collection('business_entities');

      if (filters?.category) {
        query = query.where('category', '==', filters.category);
      }

      if (filters?.status) {
        query = query.where('status', '==', filters.status);
      }

      if (filters?.lifecycleState) {
        query = query.where('lifecycleState', '==', filters.lifecycleState);
      }

      query = query.orderBy('createdAt', 'desc');

      if (filters?.limit) {
        query = query.limit(filters.limit);
      }

      const snapshot = await query.get();

      return snapshot.docs.map((doc: any) => ({
        id: doc.id,
        ...doc.data(),
      })) as BusinessEntity[];
    } catch (error) {
      logger.error('Error listing entities', { error, filters });
      throw new Error('Failed to list entities');
    }
  }

  /**
   * Update entity
   */
  async updateEntity(entityId: string, request: UpdateEntityRequest): Promise<BusinessEntity> {
    try {
      const entityRef = this.db.collection('business_entities').doc(entityId);
      const entityDoc = await entityRef.get();

      if (!entityDoc.exists) {
        throw new Error('Entity not found');
      }

      const now = new Date().toISOString();
      const updates: any = {
        ...request,
        updatedAt: now,
      };

      // Remove undefined values
      Object.keys(updates).forEach(key => {
        if (updates[key] === undefined) {
          delete updates[key];
        }
      });

      await entityRef.update(updates);

      const updatedDoc = await entityRef.get();
      const updatedEntity = { id: updatedDoc.id, ...updatedDoc.data() } as BusinessEntity;

      logger.info('Entity updated', {
        entityId,
        updatedBy: request.updatedBy,
      });

      // Publish event
      await pubsubPublisher.publishEntityEvent({
        eventType: 'entity.updated',
        entityId,
        entity: updatedEntity,
        timestamp: now,
        triggeredBy: request.updatedBy,
      });

      return updatedEntity;
    } catch (error) {
      logger.error('Error updating entity', { error, entityId, request });
      throw error;
    }
  }

  /**
   * Archive entity (soft delete)
   */
  async archiveEntity(entityId: string, archivedBy: string): Promise<void> {
    try {
      const entityRef = this.db.collection('business_entities').doc(entityId);
      const entityDoc = await entityRef.get();

      if (!entityDoc.exists) {
        throw new Error('Entity not found');
      }

      const now = new Date().toISOString();
      const updates = {
        status: 'archived',
        lifecycleState: 'archived',
        updatedAt: now,
        updatedBy: archivedBy,
      };

      await entityRef.update(updates);

      const entity = { id: entityDoc.id, ...entityDoc.data(), ...updates } as BusinessEntity;

      logger.info('Entity archived', {
        entityId,
        archivedBy,
      });

      // Publish event
      await pubsubPublisher.publishEntityEvent({
        eventType: 'entity.archived',
        entityId,
        entity,
        timestamp: now,
        triggeredBy: archivedBy,
      });

      // Archive associated tenants
      const tenantIds = entity.tenantIds || [];
      for (const tenantId of tenantIds) {
        await this.db.collection('tenants').doc(tenantId).update({
          status: 'archived',
          updatedAt: now,
        });
      }
    } catch (error) {
      logger.error('Error archiving entity', { error, entityId });
      throw error;
    }
  }
}
