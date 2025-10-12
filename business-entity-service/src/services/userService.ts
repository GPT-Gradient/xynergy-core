/**
 * User Management Service
 * Admin operations for user and tenant management
 */

import { getFirestore } from 'firebase-admin/firestore';
import { getAuth } from 'firebase-admin/auth';
import { logger } from '../utils/logger';

export interface CreateUserRequest {
  email: string;
  name: string;
  password?: string;
  globalRole?: 'super_admin' | 'admin' | 'user';
  tenantId?: string;
  role?: string;
  permissions?: string[];
  createdBy: string;
}

export interface AssignTenantRequest {
  userId: string;
  tenantId: string;
  role: string;
  permissions: string[];
  grantedBy: string;
}

export interface RemoveTenantRequest {
  userId: string;
  tenantId: string;
  removedBy: string;
}

export class UserService {
  private get db() {
    return getFirestore();
  }
  private get auth() {
    return getAuth();
  }

  /**
   * Create new user with Firebase Auth + Firestore
   */
  async createUser(request: CreateUserRequest): Promise<any> {
    try {
      // Create Firebase Auth user
      const userRecord = await this.auth.createUser({
        email: request.email,
        displayName: request.name,
        password: request.password || this.generateTemporaryPassword(),
      });

      const now = new Date().toISOString();

      // Create Firestore user document
      const userData: any = {
        uid: userRecord.uid,
        email: request.email,
        name: request.name,
        globalRole: request.globalRole || 'user',
        activeTenantId: request.tenantId || '',
        tenantRoles: {},
        createdAt: now,
        updatedAt: now,
        createdBy: request.createdBy,
      };

      // If tenant and role provided, assign immediately
      if (request.tenantId && request.role) {
        userData.tenantRoles[request.tenantId] = {
          role: request.role,
          permissions: request.permissions || [],
          grantedAt: now,
          grantedBy: request.createdBy,
        };
      }

      await this.db.collection('users').doc(userRecord.uid).set(userData);

      logger.info('User created', {
        uid: userRecord.uid,
        email: request.email,
        globalRole: userData.globalRole,
        tenantId: request.tenantId,
      });

      return {
        uid: userRecord.uid,
        email: request.email,
        name: request.name,
        globalRole: userData.globalRole,
        tenantRoles: userData.tenantRoles,
      };
    } catch (error) {
      logger.error('Error creating user', { error, request });
      throw error;
    }
  }

  /**
   * Get user by UID
   */
  async getUser(userId: string): Promise<any> {
    try {
      const doc = await this.db.collection('users').doc(userId).get();

      if (!doc.exists) {
        throw new Error('User not found');
      }

      return { uid: doc.id, ...doc.data() };
    } catch (error) {
      logger.error('Error fetching user', { error, userId });
      throw error;
    }
  }

  /**
   * List all users
   */
  async listUsers(limit: number = 100): Promise<any[]> {
    try {
      const snapshot = await this.db
        .collection('users')
        .orderBy('createdAt', 'desc')
        .limit(limit)
        .get();

      return snapshot.docs.map(doc => ({
        uid: doc.id,
        ...doc.data(),
      }));
    } catch (error) {
      logger.error('Error listing users', { error });
      throw new Error('Failed to list users');
    }
  }

  /**
   * Assign user to tenant with role
   */
  async assignTenant(request: AssignTenantRequest): Promise<void> {
    try {
      const userRef = this.db.collection('users').doc(request.userId);
      const userDoc = await userRef.get();

      if (!userDoc.exists) {
        throw new Error('User not found');
      }

      // Verify tenant exists
      const tenantDoc = await this.db.collection('tenants').doc(request.tenantId).get();
      if (!tenantDoc.exists) {
        throw new Error('Tenant not found');
      }

      const now = new Date().toISOString();

      await userRef.update({
        [`tenantRoles.${request.tenantId}`]: {
          role: request.role,
          permissions: request.permissions,
          grantedAt: now,
          grantedBy: request.grantedBy,
        },
        updatedAt: now,
      });

      logger.info('User assigned to tenant', {
        userId: request.userId,
        tenantId: request.tenantId,
        role: request.role,
      });
    } catch (error) {
      logger.error('Error assigning tenant', { error, request });
      throw error;
    }
  }

  /**
   * Remove user from tenant
   */
  async removeTenant(request: RemoveTenantRequest): Promise<void> {
    try {
      const userRef = this.db.collection('users').doc(request.userId);
      const userDoc = await userRef.get();

      if (!userDoc.exists) {
        throw new Error('User not found');
      }

      const now = new Date().toISOString();
      const userData = userDoc.data();

      // Remove tenant from tenantRoles
      const tenantRoles = userData?.tenantRoles || {};
      delete tenantRoles[request.tenantId];

      await userRef.update({
        tenantRoles,
        updatedAt: now,
      });

      logger.info('User removed from tenant', {
        userId: request.userId,
        tenantId: request.tenantId,
      });
    } catch (error) {
      logger.error('Error removing tenant', { error, request });
      throw error;
    }
  }

  /**
   * Update user's global role
   */
  async updateGlobalRole(userId: string, globalRole: string, updatedBy: string): Promise<void> {
    try {
      const userRef = this.db.collection('users').doc(userId);
      const userDoc = await userRef.get();

      if (!userDoc.exists) {
        throw new Error('User not found');
      }

      const now = new Date().toISOString();

      await userRef.update({
        globalRole,
        updatedAt: now,
        updatedBy,
      });

      logger.info('User global role updated', {
        userId,
        globalRole,
        updatedBy,
      });
    } catch (error) {
      logger.error('Error updating global role', { error, userId });
      throw error;
    }
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
