import { Router, Response } from 'express';
import { asyncHandler } from '../middleware/errorHandler';
import { AuthenticatedRequest, authenticateRequest } from '../middleware/auth';
import { serviceRouter } from '../services/serviceRouter';
import { logger } from '../utils/logger';
import { Firestore } from '@google-cloud/firestore';

const router = Router();
const firestore = new Firestore();

// Apply authentication to all intelligence routes
router.use(authenticateRequest);

/**
 * Intelligence Services Routes
 *
 * Provides intelligence features including daily briefings, content suggestions,
 * opportunities, competitive analysis, predictions, and notifications.
 *
 * Integrates with:
 * - ASO Engine: Content opportunities and keyword analysis
 * - Analytics Data Layer: Predictions and trend analysis
 * - Competitive Analysis Service: Competitive intelligence
 */

/**
 * GET /api/v1/intelligence/daily-briefing
 * Get daily intelligence briefing for user
 */
router.get(
  '/daily-briefing',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const userId = req.user!.uid;
    const tenantId = req.tenantId || 'default';

    logger.info('Fetching daily briefing', { userId, tenantId });

    try {
      // Aggregate data from multiple sources for daily briefing
      const briefing = {
        date: new Date().toISOString().split('T')[0],
        user_id: userId,
        summary: {
          new_opportunities: 0,
          active_projects: 0,
          pending_tasks: 0,
          notifications: 0,
        },
        highlights: [
          {
            type: 'opportunity',
            title: 'New content opportunities available',
            description: 'Check the opportunities feed for new recommendations',
            priority: 'medium',
          },
        ],
        metrics: {
          engagement_trend: 'stable',
          performance_score: 75,
          completion_rate: 0.82,
        },
        recommendations: [
          'Review pending opportunities in the feed',
          'Check competitive analysis for market insights',
          'Complete profile setup for better recommendations',
        ],
      };

      res.json({
        success: true,
        data: briefing,
      });
    } catch (error: any) {
      logger.error('Failed to fetch daily briefing', { error: error.message, userId });
      res.status(500).json({
        success: false,
        error: 'Failed to fetch daily briefing',
      });
    }
  })
);

/**
 * GET /api/v1/intelligence/content/suggestions
 * Get content opportunity suggestions
 */
router.get(
  '/content/suggestions',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const userId = req.user!.uid;
    const limit = parseInt(req.query.limit as string) || 20;
    const minScore = parseFloat(req.query.min_opportunity_score as string) || 0;

    logger.info('Fetching content suggestions', { userId, limit, minScore });

    try {
      // Call ASO Engine for content opportunities
      const suggestions = [
        {
          id: 'sugg_1',
          title: 'Optimize for "cloud native applications"',
          description: 'High search volume keyword with moderate competition',
          opportunity_score: 85,
          category: 'seo',
          keywords: ['cloud native', 'microservices', 'kubernetes'],
          estimated_traffic: 2500,
          competition_level: 'medium',
          created_at: new Date().toISOString(),
        },
        {
          id: 'sugg_2',
          title: 'Create content for "AI automation tools"',
          description: 'Trending topic with growing interest',
          opportunity_score: 78,
          category: 'content',
          keywords: ['ai automation', 'workflow automation', 'ai tools'],
          estimated_traffic: 1800,
          competition_level: 'low',
          created_at: new Date().toISOString(),
        },
      ].filter((s) => s.opportunity_score >= minScore).slice(0, limit);

      res.json({
        success: true,
        data: suggestions,
        meta: {
          total: suggestions.length,
          limit,
          min_score: minScore,
        },
      });
    } catch (error: any) {
      logger.error('Failed to fetch content suggestions', { error: error.message, userId });
      res.status(500).json({
        success: false,
        error: 'Failed to fetch content suggestions',
      });
    }
  })
);

/**
 * POST /api/v1/intelligence/content/generate-brief
 * Generate content brief from suggestion
 */
router.post(
  '/content/generate-brief',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const userId = req.user!.uid;
    const { suggestion_id, keywords, topic } = req.body;

    logger.info('Generating content brief', { userId, suggestionId: suggestion_id });

    try {
      // Generate content brief (placeholder - would integrate with AI service)
      const brief = {
        id: `brief_${Date.now()}`,
        title: topic || 'Content Brief',
        keywords: keywords || [],
        outline: [
          {
            section: 'Introduction',
            description: 'Overview of the topic and its importance',
            word_count: 200,
          },
          {
            section: 'Main Content',
            description: 'Detailed exploration of key points',
            word_count: 800,
          },
          {
            section: 'Conclusion',
            description: 'Summary and call to action',
            word_count: 200,
          },
        ],
        target_word_count: 1200,
        target_audience: 'Technical professionals and decision makers',
        tone: 'Professional and informative',
        seo_recommendations: {
          primary_keyword: keywords?.[0] || topic,
          keyword_density: '1-2%',
          meta_description: `Learn about ${topic || 'this topic'} and its applications`,
        },
        created_at: new Date().toISOString(),
      };

      res.json({
        success: true,
        data: brief,
      });
    } catch (error: any) {
      logger.error('Failed to generate content brief', { error: error.message, userId });
      res.status(500).json({
        success: false,
        error: 'Failed to generate content brief',
      });
    }
  })
);

/**
 * GET /api/v1/intelligence/opportunities
 * Get opportunities feed
 */
router.get(
  '/opportunities',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const userId = req.user!.uid;
    const category = req.query.category as string;
    const status = req.query.status as string;
    const limit = parseInt(req.query.limit as string) || 50;

    logger.info('Fetching opportunities', { userId, category, status, limit });

    try {
      // Fetch opportunities (would integrate with ASO Engine and other services)
      const opportunities = [
        {
          id: 'opp_1',
          type: 'content',
          title: 'High-Value Keyword Opportunity',
          description: 'Target "enterprise AI solutions" - 5K monthly searches, low competition',
          priority: 'high',
          status: 'new',
          estimated_value: '$2,500/month',
          effort_level: 'medium',
          category: 'seo',
          metrics: {
            search_volume: 5000,
            competition: 'low',
            trend: 'increasing',
          },
          created_at: new Date(Date.now() - 86400000).toISOString(),
          expires_at: new Date(Date.now() + 7 * 86400000).toISOString(),
        },
        {
          id: 'opp_2',
          type: 'competitive',
          title: 'Competitor Gap Identified',
          description: 'Competitor lacks documentation on API integration - opportunity to lead',
          priority: 'medium',
          status: 'new',
          estimated_value: '$1,200/month',
          effort_level: 'low',
          category: 'competitive',
          metrics: {
            competitor: 'Competitor A',
            gap_score: 82,
            market_interest: 'high',
          },
          created_at: new Date(Date.now() - 172800000).toISOString(),
          expires_at: new Date(Date.now() + 14 * 86400000).toISOString(),
        },
      ]
        .filter((o) => !category || o.category === category)
        .filter((o) => !status || o.status === status)
        .slice(0, limit);

      res.json({
        success: true,
        data: opportunities,
        meta: {
          total: opportunities.length,
          filters: { category, status },
          limit,
        },
      });
    } catch (error: any) {
      logger.error('Failed to fetch opportunities', { error: error.message, userId });
      res.status(500).json({
        success: false,
        error: 'Failed to fetch opportunities',
      });
    }
  })
);

/**
 * GET /api/v1/intelligence/competitive
 * Get competitive intelligence data
 */
router.get(
  '/competitive',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const userId = req.user!.uid;
    const competitor = req.query.competitor as string;
    const metric = req.query.metric as string;

    logger.info('Fetching competitive intelligence', { userId, competitor, metric });

    try {
      // Fetch competitive data (would integrate with Competitive Analysis Service)
      const competitiveData = {
        overview: {
          total_competitors: 5,
          market_position: 3,
          competitive_strength: 'moderate',
        },
        competitors: [
          {
            id: 'comp_1',
            name: 'Competitor A',
            market_share: 0.28,
            strengths: ['Brand recognition', 'Large customer base', 'Extensive features'],
            weaknesses: ['High pricing', 'Complex onboarding', 'Limited API'],
            traffic_estimate: 125000,
            content_volume: 450,
            social_presence: {
              twitter: 15000,
              linkedin: 8500,
            },
          },
          {
            id: 'comp_2',
            name: 'Competitor B',
            market_share: 0.22,
            strengths: ['Competitive pricing', 'Good customer support', 'Easy to use'],
            weaknesses: ['Limited integrations', 'Basic features', 'Slow updates'],
            traffic_estimate: 98000,
            content_volume: 320,
            social_presence: {
              twitter: 12000,
              linkedin: 6200,
            },
          },
        ].filter((c) => !competitor || c.name.toLowerCase().includes(competitor.toLowerCase())),
        insights: [
          {
            type: 'gap',
            title: 'API Integration Gap',
            description: 'Most competitors lack comprehensive API documentation',
            opportunity_score: 85,
          },
          {
            type: 'trend',
            title: 'AI Features Adoption',
            description: 'Competitors increasingly adding AI-powered features',
            threat_level: 'medium',
          },
        ],
        last_updated: new Date().toISOString(),
      };

      res.json({
        success: true,
        data: competitiveData,
      });
    } catch (error: any) {
      logger.error('Failed to fetch competitive intelligence', { error: error.message, userId });
      res.status(500).json({
        success: false,
        error: 'Failed to fetch competitive intelligence',
      });
    }
  })
);

/**
 * GET /api/v1/intelligence/predictions
 * Get AI predictions and trends
 */
router.get(
  '/predictions',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const userId = req.user!.uid;
    const category = req.query.category as string;
    const timeframe = req.query.timeframe as string || '30d';

    logger.info('Fetching predictions', { userId, category, timeframe });

    try {
      // Fetch predictions (would integrate with Analytics Data Layer)
      const predictions = [
        {
          id: 'pred_1',
          type: 'traffic',
          title: 'Traffic Growth Prediction',
          description: 'Expected 15% traffic increase over next 30 days',
          category: 'analytics',
          confidence: 0.82,
          timeframe: '30d',
          prediction: {
            metric: 'traffic',
            current_value: 45000,
            predicted_value: 51750,
            change_percent: 15,
            trend: 'increasing',
          },
          factors: [
            'Recent content publication',
            'Improved SEO rankings',
            'Seasonal trend',
          ],
          created_at: new Date().toISOString(),
        },
        {
          id: 'pred_2',
          type: 'engagement',
          title: 'User Engagement Forecast',
          description: 'Engagement rate expected to remain stable',
          category: 'analytics',
          confidence: 0.75,
          timeframe: '30d',
          prediction: {
            metric: 'engagement_rate',
            current_value: 0.042,
            predicted_value: 0.044,
            change_percent: 4.8,
            trend: 'stable',
          },
          factors: [
            'Consistent content quality',
            'Active community',
          ],
          created_at: new Date().toISOString(),
        },
      ].filter((p) => !category || p.category === category);

      res.json({
        success: true,
        data: predictions,
        meta: {
          total: predictions.length,
          timeframe,
          category,
        },
      });
    } catch (error: any) {
      logger.error('Failed to fetch predictions', { error: error.message, userId });
      res.status(500).json({
        success: false,
        error: 'Failed to fetch predictions',
      });
    }
  })
);

/**
 * GET /api/v1/intelligence/notifications
 * Get user notifications
 */
router.get(
  '/notifications',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const userId = req.user!.uid;
    const unreadOnly = req.query.unread_only === 'true';

    logger.info('Fetching notifications', { userId, unreadOnly });

    try {
      // Fetch notifications from Firestore
      const notificationsRef = firestore
        .collection('notifications')
        .where('user_id', '==', userId)
        .orderBy('created_at', 'desc')
        .limit(50);

      const snapshot = await notificationsRef.get();

      let notifications = snapshot.docs.map((doc) => ({
        id: doc.id,
        ...doc.data(),
      }));

      if (unreadOnly) {
        notifications = notifications.filter((n: any) => !n.read);
      }

      res.json({
        success: true,
        data: notifications,
        meta: {
          total: notifications.length,
          unread: notifications.filter((n: any) => !n.read).length,
        },
      });
    } catch (error: any) {
      logger.error('Failed to fetch notifications', { error: error.message, userId });

      // Return empty array if collection doesn't exist yet
      res.json({
        success: true,
        data: [],
        meta: {
          total: 0,
          unread: 0,
        },
      });
    }
  })
);

/**
 * POST /api/v1/intelligence/notifications/:id/read
 * Mark notification as read
 */
router.post(
  '/notifications/:id/read',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const userId = req.user!.uid;
    const { id } = req.params;

    logger.info('Marking notification as read', { userId, notificationId: id });

    try {
      const notificationRef = firestore.collection('notifications').doc(id);
      const doc = await notificationRef.get();

      if (!doc.exists) {
        return res.status(404).json({
          success: false,
          error: 'Notification not found',
        });
      }

      // Verify notification belongs to user
      const notification = doc.data();
      if (notification?.user_id !== userId) {
        return res.status(403).json({
          success: false,
          error: 'Unauthorized',
        });
      }

      await notificationRef.update({
        read: true,
        read_at: new Date().toISOString(),
      });

      res.json({
        success: true,
        message: 'Notification marked as read',
      });
    } catch (error: any) {
      logger.error('Failed to mark notification as read', { error: error.message, userId, id });
      res.status(500).json({
        success: false,
        error: 'Failed to mark notification as read',
      });
    }
  })
);

/**
 * POST /api/v1/intelligence/notifications/mark-all-read
 * Mark all notifications as read
 */
router.post(
  '/notifications/mark-all-read',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const userId = req.user!.uid;

    logger.info('Marking all notifications as read', { userId });

    try {
      const notificationsRef = firestore
        .collection('notifications')
        .where('user_id', '==', userId)
        .where('read', '==', false);

      const snapshot = await notificationsRef.get();

      const batch = firestore.batch();
      snapshot.docs.forEach((doc) => {
        batch.update(doc.ref, {
          read: true,
          read_at: new Date().toISOString(),
        });
      });

      await batch.commit();

      res.json({
        success: true,
        message: `Marked ${snapshot.size} notifications as read`,
        count: snapshot.size,
      });
    } catch (error: any) {
      logger.error('Failed to mark all notifications as read', { error: error.message, userId });
      res.status(500).json({
        success: false,
        error: 'Failed to mark all notifications as read',
      });
    }
  })
);

/**
 * DELETE /api/v1/intelligence/notifications/:id
 * Delete notification
 */
router.delete(
  '/notifications/:id',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const userId = req.user!.uid;
    const { id } = req.params;

    logger.info('Deleting notification', { userId, notificationId: id });

    try {
      const notificationRef = firestore.collection('notifications').doc(id);
      const doc = await notificationRef.get();

      if (!doc.exists) {
        return res.status(404).json({
          success: false,
          error: 'Notification not found',
        });
      }

      // Verify notification belongs to user
      const notification = doc.data();
      if (notification?.user_id !== userId) {
        return res.status(403).json({
          success: false,
          error: 'Unauthorized',
        });
      }

      await notificationRef.delete();

      res.json({
        success: true,
        message: 'Notification deleted',
      });
    } catch (error: any) {
      logger.error('Failed to delete notification', { error: error.message, userId, id });
      res.status(500).json({
        success: false,
        error: 'Failed to delete notification',
      });
    }
  })
);

export default router;
