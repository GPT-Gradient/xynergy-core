"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const firestore_1 = require("@google-cloud/firestore");
const errorHandler_1 = require("../middleware/errorHandler");
const auth_1 = require("../middleware/auth");
const logger_1 = require("../utils/logger");
const router = (0, express_1.Router)();
const firestore = new firestore_1.Firestore();
// Apply authentication to all profile routes
router.use(auth_1.authenticateRequest);
/**
 * GET /api/v1/profile
 *
 * Load user profile
 */
router.get('/', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const userId = req.user.uid;
    try {
        const profileRef = firestore.collection('profiles').doc(userId);
        const profileDoc = await profileRef.get();
        if (!profileDoc.exists) {
            // Create default profile if it doesn't exist
            const defaultProfile = createDefaultProfile(userId, req.user);
            await profileRef.set(defaultProfile);
            logger_1.logger.info('Created default profile for user', { userId });
            return res.json({
                success: true,
                data: defaultProfile,
            });
        }
        const profileData = profileDoc.data();
        logger_1.logger.info('Profile loaded', { userId });
        res.json({
            success: true,
            data: profileData,
        });
    }
    catch (error) {
        logger_1.logger.error('Failed to load profile', { error, userId });
        res.status(500).json({
            success: false,
            error: 'Failed to load profile',
        });
    }
}));
/**
 * PUT /api/v1/profile
 *
 * Update user profile (full or partial update)
 */
router.put('/', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const userId = req.user.uid;
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
            const defaultProfile = createDefaultProfile(userId, req.user);
            const newProfile = {
                ...defaultProfile,
                ...updates,
                user_id: userId, // Ensure user_id cannot be changed
                updated_at: new Date().toISOString(),
            };
            await profileRef.set(newProfile);
            logger_1.logger.info('Created profile with updates', { userId });
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
        const updatedProfile = updatedDoc.data();
        logger_1.logger.info('Profile updated', { userId, fields: Object.keys(updates) });
        res.json({
            success: true,
            data: updatedProfile,
        });
    }
    catch (error) {
        logger_1.logger.error('Failed to update profile', { error, userId });
        res.status(500).json({
            success: false,
            error: 'Failed to update profile',
        });
    }
}));
/**
 * POST /api/v1/profile/conversation
 *
 * Add conversation to history
 */
router.post('/conversation', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const userId = req.user.uid;
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
        const conversation = {
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
        let profile;
        if (!profileDoc.exists) {
            // Create profile with conversation
            profile = createDefaultProfile(userId, req.user);
            profile.conversation_history = [conversation];
            profile.updated_at = new Date().toISOString();
            await profileRef.set(profile);
            logger_1.logger.info('Created profile with conversation', { userId });
        }
        else {
            // Get existing profile and append conversation
            profile = profileDoc.data();
            const conversationHistory = profile.conversation_history || [];
            // Add new conversation at the beginning, limit to 100
            profile.conversation_history = [conversation, ...conversationHistory].slice(0, 100);
            profile.updated_at = new Date().toISOString();
            // Update with full profile to ensure conversation_history exists
            await profileRef.set(profile, { merge: true });
            logger_1.logger.info('Conversation added to profile', { userId, conversationId: conversation.conversation_id });
        }
        res.json({
            success: true,
            data: conversation,
        });
    }
    catch (error) {
        logger_1.logger.error('Failed to add conversation', { error: error.message, stack: error.stack, userId });
        res.status(500).json({
            success: false,
            error: 'Failed to add conversation',
            details: error.message,
        });
    }
}));
/**
 * DELETE /api/v1/profile
 *
 * Delete user profile (optional - for GDPR compliance)
 */
router.delete('/', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const userId = req.user.uid;
    try {
        const profileRef = firestore.collection('profiles').doc(userId);
        await profileRef.delete();
        logger_1.logger.info('Profile deleted', { userId });
        res.json({
            success: true,
            message: 'Profile deleted successfully',
        });
    }
    catch (error) {
        logger_1.logger.error('Failed to delete profile', { error, userId });
        res.status(500).json({
            success: false,
            error: 'Failed to delete profile',
        });
    }
}));
/**
 * Helper: Create default profile
 */
function createDefaultProfile(userId, user) {
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
exports.default = router;
//# sourceMappingURL=profile.js.map