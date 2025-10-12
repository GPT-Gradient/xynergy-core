/**
 * Beta Application Routes
 */

import { Router, Request, Response } from 'express';
import { ApplicationService } from '../services/applicationService';
import { logger } from '../utils/logger';

const router = Router();
const applicationService = new ApplicationService();

/**
 * POST /api/v1/beta/applications
 * Submit beta application (public)
 */
router.post('/', async (req: Request, res: Response) => {
  try {
    const { email, name, company, role, linkedinUrl, twitterHandle, reason, experience, referralSource, phase } = req.body;

    if (!email || !name || !reason) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'email, name, and reason are required',
        },
      });
    }

    const application = await applicationService.submitApplication({
      email,
      name,
      company,
      role,
      linkedinUrl,
      twitterHandle,
      reason,
      experience,
      referralSource,
      phase,
    });

    res.status(201).json({
      success: true,
      data: application,
      message: 'Application submitted successfully',
    });
  } catch (error: any) {
    logger.error('Error in POST /applications', { error });

    const statusCode = error.message.includes('already submitted') ? 409 : 500;
    res.status(statusCode).json({
      success: false,
      error: {
        code: statusCode === 409 ? 'DUPLICATE_APPLICATION' : 'APPLICATION_SUBMIT_FAILED',
        message: error.message || 'Failed to submit application',
      },
    });
  }
});

/**
 * GET /api/v1/beta/applications
 * List all applications (admin)
 */
router.get('/', async (req: Request, res: Response) => {
  try {
    const { status, phase, limit } = req.query;

    const applications = await applicationService.listApplications({
      status: status as string,
      phase: phase as string,
      limit: limit ? parseInt(limit as string) : undefined,
    });

    res.json({
      success: true,
      data: applications,
      count: applications.length,
    });
  } catch (error: any) {
    logger.error('Error in GET /applications', { error });
    res.status(500).json({
      success: false,
      error: {
        code: 'APPLICATION_LIST_FAILED',
        message: error.message || 'Failed to list applications',
      },
    });
  }
});

/**
 * GET /api/v1/beta/applications/:id
 * Get application by ID (admin)
 */
router.get('/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;

    const application = await applicationService.getApplication(id);

    if (!application) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'APPLICATION_NOT_FOUND',
          message: 'Application not found',
        },
      });
    }

    res.json({
      success: true,
      data: application,
    });
  } catch (error: any) {
    logger.error('Error in GET /applications/:id', { error });
    res.status(500).json({
      success: false,
      error: {
        code: 'APPLICATION_FETCH_FAILED',
        message: error.message || 'Failed to fetch application',
      },
    });
  }
});

/**
 * POST /api/v1/beta/applications/:id/approve
 * Approve application (admin)
 */
router.post('/:id/approve', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { approvedBy, tenantId, notes, customPermissions } = req.body;

    if (!approvedBy) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'approvedBy is required',
        },
      });
    }

    const result = await applicationService.approveApplication({
      applicationId: id,
      approvedBy,
      tenantId,
      notes,
      customPermissions,
    });

    res.json({
      success: true,
      data: result,
      message: 'Application approved successfully',
    });
  } catch (error: any) {
    logger.error('Error in POST /applications/:id/approve', { error });

    const statusCode = error.message.includes('not found') ? 404 : 400;
    res.status(statusCode).json({
      success: false,
      error: {
        code: statusCode === 404 ? 'APPLICATION_NOT_FOUND' : 'APPROVAL_FAILED',
        message: error.message || 'Failed to approve application',
      },
    });
  }
});

/**
 * POST /api/v1/beta/applications/:id/reject
 * Reject application (admin)
 */
router.post('/:id/reject', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { rejectedBy, reason, notes } = req.body;

    if (!rejectedBy) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'rejectedBy is required',
        },
      });
    }

    const application = await applicationService.rejectApplication({
      applicationId: id,
      rejectedBy,
      reason,
      notes,
    });

    res.json({
      success: true,
      data: application,
      message: 'Application rejected',
    });
  } catch (error: any) {
    logger.error('Error in POST /applications/:id/reject', { error });

    const statusCode = error.message.includes('not found') ? 404 : 400;
    res.status(statusCode).json({
      success: false,
      error: {
        code: statusCode === 404 ? 'APPLICATION_NOT_FOUND' : 'REJECTION_FAILED',
        message: error.message || 'Failed to reject application',
      },
    });
  }
});

/**
 * POST /api/v1/beta/applications/:id/waitlist
 * Move application to waitlist (admin)
 */
router.post('/:id/waitlist', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { processedBy } = req.body;

    if (!processedBy) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'processedBy is required',
        },
      });
    }

    const application = await applicationService.waitlistApplication(id, processedBy);

    res.json({
      success: true,
      data: application,
      message: 'Application moved to waitlist',
    });
  } catch (error: any) {
    logger.error('Error in POST /applications/:id/waitlist', { error });

    const statusCode = error.message.includes('not found') ? 404 : 400;
    res.status(statusCode).json({
      success: false,
      error: {
        code: statusCode === 404 ? 'APPLICATION_NOT_FOUND' : 'WAITLIST_FAILED',
        message: error.message || 'Failed to move to waitlist',
      },
    });
  }
});

/**
 * POST /api/v1/beta/applications/batch-approve
 * Batch approve applications (admin)
 */
router.post('/batch-approve', async (req: Request, res: Response) => {
  try {
    const { applicationIds, approvedBy, tenantId } = req.body;

    if (!applicationIds || !Array.isArray(applicationIds) || applicationIds.length === 0) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'applicationIds array is required',
        },
      });
    }

    if (!approvedBy) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'approvedBy is required',
        },
      });
    }

    const result = await applicationService.batchApprove({
      applicationIds,
      approvedBy,
      tenantId,
    });

    res.json({
      success: true,
      data: result,
      message: `Batch approval completed: ${result.successful.length} successful, ${result.failed.length} failed`,
    });
  } catch (error: any) {
    logger.error('Error in POST /applications/batch-approve', { error });
    res.status(500).json({
      success: false,
      error: {
        code: 'BATCH_APPROVAL_FAILED',
        message: error.message || 'Failed to batch approve applications',
      },
    });
  }
});

export default router;
