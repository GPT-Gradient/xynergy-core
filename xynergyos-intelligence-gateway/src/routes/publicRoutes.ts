import { Router, Request, Response } from 'express';
import { validateApiKey } from '../middleware/apiKeyAuth';
import { publicRouteRateLimit } from '../middleware/rateLimit';
import { getFirestore } from '../config/firebase';
import { logger } from '../utils/logger';

const router = Router();
const db = getFirestore();

// Apply middleware to all public routes
router.use(validateApiKey);
router.use(publicRouteRateLimit);

/**
 * POST /api/public/beta
 * Submit beta program application from website
 */
router.post('/beta', async (req: Request, res: Response) => {
  try {
    const {
      company_name,
      contact_name,
      email,
      industry,
      phone,
      website,
      goals,
      interests,
      referred_by
    } = req.body;

    // Validation
    if (!company_name || !contact_name || !email || !industry || !goals) {
      logger.warn('Beta application validation failed: Missing required fields', {
        ip: req.ip,
        body: req.body,
      });
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: company_name, contact_name, email, industry, goals'
      });
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      logger.warn('Beta application validation failed: Invalid email', {
        ip: req.ip,
        email,
      });
      return res.status(400).json({
        success: false,
        error: 'Invalid email address'
      });
    }

    // Create application document
    const applicationData = {
      company_name,
      contact_name,
      email,
      industry,
      phone: phone || null,
      website: website || null,
      goals,
      interests: interests || [],
      referred_by: referred_by || null,
      status: 'pending',
      source: 'website',
      submitted_at: new Date().toISOString(),
      created_at: new Date().toISOString(),
      ip_address: req.ip || 'unknown',
    };

    const applicationRef = await db.collection('beta_applications').add(applicationData);

    logger.info('Beta application submitted successfully', {
      applicationId: applicationRef.id,
      email,
      company: company_name,
    });

    // TODO: Send notification to team (Slack/Email)

    res.status(200).json({
      success: true,
      application_id: applicationRef.id,
      message: 'Application submitted successfully'
    });

  } catch (error) {
    logger.error('Error submitting beta application', {
      error: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : undefined,
    });
    res.status(500).json({
      success: false,
      error: 'Failed to submit application'
    });
  }
});

/**
 * POST /api/public/contact
 * Submit contact form from website
 */
router.post('/contact', async (req: Request, res: Response) => {
  try {
    const { name, email, message, phone, company } = req.body;

    // Validation
    if (!name || !email || !message) {
      logger.warn('Contact form validation failed: Missing required fields', {
        ip: req.ip,
        body: req.body,
      });
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: name, email, message'
      });
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      logger.warn('Contact form validation failed: Invalid email', {
        ip: req.ip,
        email,
      });
      return res.status(400).json({
        success: false,
        error: 'Invalid email address'
      });
    }

    // Message length validation
    if (message.length < 10) {
      logger.warn('Contact form validation failed: Message too short', {
        ip: req.ip,
        messageLength: message.length,
      });
      return res.status(400).json({
        success: false,
        error: 'Message must be at least 10 characters long'
      });
    }

    if (message.length > 5000) {
      logger.warn('Contact form validation failed: Message too long', {
        ip: req.ip,
        messageLength: message.length,
      });
      return res.status(400).json({
        success: false,
        error: 'Message must not exceed 5000 characters'
      });
    }

    // Create contact submission
    const submissionData = {
      name,
      email,
      message,
      phone: phone || null,
      company: company || null,
      status: 'new',
      source: 'website',
      submitted_at: new Date().toISOString(),
      created_at: new Date().toISOString(),
      ip_address: req.ip || 'unknown',
    };

    const submissionRef = await db.collection('contact_submissions').add(submissionData);

    logger.info('Contact form submitted successfully', {
      submissionId: submissionRef.id,
      email,
      name,
    });

    // TODO: Send notification to team (Slack/Email)

    res.status(200).json({
      success: true,
      submission_id: submissionRef.id,
      message: 'Message sent successfully'
    });

  } catch (error) {
    logger.error('Error submitting contact form', {
      error: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : undefined,
    });
    res.status(500).json({
      success: false,
      error: 'Failed to send message'
    });
  }
});

export default router;
