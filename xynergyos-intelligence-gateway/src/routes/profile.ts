import { Router, Response } from 'express';
import { Firestore } from '@google-cloud/firestore';
import { asyncHandler } from '../middleware/errorHandler';
import { AuthenticatedRequest, authenticateRequest } from '../middleware/auth';
import { logger } from '../utils/logger';

const router = Router();
const firestore = new Firestore();

// Apply authentication to all profile routes
router.use(authenticateRequest);

/**
 * User Profile Management Routes
 *
 * Manages user profiles with communication preferences, business context,
 * and conversation history
 */

interface CommunicationStyle {
  preferred_output_format: string;
  technical_level: string;
  decision_style: string;
}

interface BusinessContext {
  active_projects: string[];
  roles: string[];
  preferences: string[];
}

interface VoicePatterns {
  typical_memo_length: string;
  speaking_pace: string;
  preferred_commands: string[];
  context_switching_frequency: string;
}

interface ProjectContext {
  current_focus: string | null;
  recent_activities: Array<{
    type: string;
    timestamp: string;
    summary: string;
    projects?: string[];
  }>;
  priority_matrix: Record<string, number>;
}

interface Conversation {
  conversation_id: string;
  timestamp: string;
  context: string;
  ai_response: string;
  outcome?: string;
  projects_affected: string[];
}

interface UserProfile {
  user_id: string;
  communication_style: CommunicationStyle;
  business_context: BusinessContext;
  conversation_history: Conversation[];
  voice_patterns: VoicePatterns;
  project_context: ProjectContext;
  created_at: string;
  updated_at: string;
}

/**
 * GET /api/v1/profile
 *
 * Load user profile
 */
router.get(
  '/',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const userId = req.user!.uid;

    try {
      const profileRef = firestore.collection('profiles').doc(userId);
      const profileDoc = await profileRef.get();

      if (!profileDoc.exists) {
        // Create default profile if it doesn't exist
        const defaultProfile = createDefaultProfile(userId, req.user!);

        await profileRef.set(defaultProfile);

        logger.info('Created default profile for user', { userId });

        return res.json({
          success: true,
          data: defaultProfile,
        });
      }

      const profileData = profileDoc.data() as UserProfile;

      logger.info('Profile loaded', { userId });

      res.json({
        success: true,
        data: profileData,
      });
    } catch (error) {
      logger.error('Failed to load profile', { error, userId });
      res.status(500).json({
        success: false,
        error: 'Failed to load profile',
      });
    }
  })
);

/**
 * PUT /api/v1/profile
 *
 * Update user profile (full or partial update)
 */
router.put(
  '/',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const userId = req.user!.uid;
    const updates = req.body;

    if (!updates || Object.keys(updates).length === 0) {
      return res.status(400).json({
        success: false,
        error: 'No updates provided',
      });
    }

    try {
      const profileRef = firestore.collection('profiles').doc(userId);
      const profileDoc = await profileRef.get();

      if (!profileDoc.exists) {
        // Create profile if it doesn't exist
        const defaultProfile = createDefaultProfile(userId, req.user!);
        const newProfile = {
          ...defaultProfile,
          ...updates,
          user_id: userId, // Ensure user_id cannot be changed
          updated_at: new Date().toISOString(),
        };

        await profileRef.set(newProfile);

        logger.info('Created profile with updates', { userId });

        return res.json({
          success: true,
          data: newProfile,
        });
      }

      // Update existing profile
      const updatedData = {
        ...updates,
        user_id: userId, // Ensure user_id cannot be changed
        updated_at: new Date().toISOString(),
      };

      await profileRef.update(updatedData);

      // Fetch updated profile
      const updatedDoc = await profileRef.get();
      const updatedProfile = updatedDoc.data() as UserProfile;

      logger.info('Profile updated', { userId, fields: Object.keys(updates) });

      res.json({
        success: true,
        data: updatedProfile,
      });
    } catch (error) {
      logger.error('Failed to update profile', { error, userId });
      res.status(500).json({
        success: false,
        error: 'Failed to update profile',
      });
    }
  })
);

/**
 * POST /api/v1/profile/conversation
 *
 * Add conversation to history
 */
router.post(
  '/conversation',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const userId = req.user!.uid;
    const conversationData = req.body;

    // Validation
    if (!conversationData.context || !conversationData.ai_response) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: context, ai_response',
      });
    }

    try {
      const profileRef = firestore.collection('profiles').doc(userId);
      const profileDoc = await profileRef.get();

      // Create conversation entry (remove undefined fields for Firestore)
      const conversation: any = {
        conversation_id: conversationData.conversation_id || `conv_${Date.now()}`,
        timestamp: conversationData.timestamp || new Date().toISOString(),
        context: conversationData.context,
        ai_response: conversationData.ai_response,
        projects_affected: conversationData.projects_affected || [],
      };

      // Only add outcome if provided
      if (conversationData.outcome !== undefined) {
        conversation.outcome = conversationData.outcome;
      }

      let profile: UserProfile;

      if (!profileDoc.exists) {
        // Create profile with conversation
        profile = createDefaultProfile(userId, req.user!);
        profile.conversation_history = [conversation];
        profile.updated_at = new Date().toISOString();

        await profileRef.set(profile);

        logger.info('Created profile with conversation', { userId });
      } else {
        // Get existing profile and append conversation
        profile = profileDoc.data() as UserProfile;
        const conversationHistory = profile.conversation_history || [];

        // Add new conversation at the beginning, limit to 100
        profile.conversation_history = [conversation, ...conversationHistory].slice(0, 100);
        profile.updated_at = new Date().toISOString();

        // Update with full profile to ensure conversation_history exists
        await profileRef.set(profile, { merge: true });

        logger.info('Conversation added to profile', { userId, conversationId: conversation.conversation_id });
      }

      res.json({
        success: true,
        data: conversation,
      });
    } catch (error: any) {
      logger.error('Failed to add conversation', { error: error.message, stack: error.stack, userId });
      res.status(500).json({
        success: false,
        error: 'Failed to add conversation',
        details: error.message,
      });
    }
  })
);

/**
 * DELETE /api/v1/profile
 *
 * Delete user profile (optional - for GDPR compliance)
 */
router.delete(
  '/',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const userId = req.user!.uid;

    try {
      const profileRef = firestore.collection('profiles').doc(userId);
      await profileRef.delete();

      logger.info('Profile deleted', { userId });

      res.json({
        success: true,
        message: 'Profile deleted successfully',
      });
    } catch (error) {
      logger.error('Failed to delete profile', { error, userId });
      res.status(500).json({
        success: false,
        error: 'Failed to delete profile',
      });
    }
  })
);

/**
 * Helper: Create default profile
 */
function createDefaultProfile(userId: string, user: { email?: string; name?: string }): UserProfile {
  return {
    user_id: userId,
    communication_style: {
      preferred_output_format: 'direct_actionable',
      technical_level: 'intermediate',
      decision_style: 'balanced',
    },
    business_context: {
      active_projects: [],
      roles: ['user'],
      preferences: [],
    },
    conversation_history: [],
    voice_patterns: {
      typical_memo_length: '2-5_minutes',
      speaking_pace: 'moderate',
      preferred_commands: [],
      context_switching_frequency: 'moderate',
    },
    project_context: {
      current_focus: null,
      recent_activities: [
        {
          type: 'profile_created',
          timestamp: new Date().toISOString(),
          summary: 'User profile initialized',
        },
      ],
      priority_matrix: {},
    },
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };
}

export default router;
