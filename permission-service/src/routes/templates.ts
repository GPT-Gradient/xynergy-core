/**
 * Permission Template Routes
 * API endpoints for managing permission templates
 */

import { Router, Request, Response } from 'express';
import { getFirestore } from 'firebase-admin/firestore';
import { logger } from '../utils/logger';

const router = Router();

/**
 * POST /api/v1/permissions/templates
 * Create new permission template
 */
router.post('/', async (req: Request, res: Response) => {
  try {
    const { name, description, permissions, targetRole, createdBy } = req.body;

    if (!name || !permissions || !targetRole || !createdBy) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'INVALID_REQUEST',
          message: 'name, permissions, targetRole, and createdBy are required',
        },
      });
    }

    const db = getFirestore();
    const templateRef = db.collection('permission_templates').doc();

    const template = {
      id: templateRef.id,
      name,
      description: description || '',
      permissions,
      targetRole,
      isSystemTemplate: false,
      createdBy,
      createdAt: new Date().toISOString(),
    };

    await templateRef.set(template);

    logger.info('Permission template created', { templateId: template.id, name });

    res.json({
      success: true,
      data: template,
    });
  } catch (error) {
    logger.error('Error creating template', { error });
    res.status(500).json({
      success: false,
      error: {
        code: 'CREATE_ERROR',
        message: 'Error creating template',
      },
    });
  }
});

/**
 * GET /api/v1/permissions/templates
 * List all permission templates
 */
router.get('/', async (req: Request, res: Response) => {
  try {
    const db = getFirestore();
    const snapshot = await db.collection('permission_templates').get();

    const templates = snapshot.docs.map(doc => doc.data());

    res.json({
      success: true,
      data: templates,
    });
  } catch (error) {
    logger.error('Error listing templates', { error });
    res.status(500).json({
      success: false,
      error: {
        code: 'LIST_ERROR',
        message: 'Error listing templates',
      },
    });
  }
});

/**
 * GET /api/v1/permissions/templates/:id
 * Get template by ID
 */
router.get('/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;

    const db = getFirestore();
    const doc = await db.collection('permission_templates').doc(id).get();

    if (!doc.exists) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'TEMPLATE_NOT_FOUND',
          message: 'Template not found',
        },
      });
    }

    res.json({
      success: true,
      data: doc.data(),
    });
  } catch (error) {
    logger.error('Error fetching template', { error });
    res.status(500).json({
      success: false,
      error: {
        code: 'FETCH_ERROR',
        message: 'Error fetching template',
      },
    });
  }
});

export default router;
