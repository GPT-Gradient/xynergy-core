"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const auth_1 = require("../middleware/auth");
const errorHandler_1 = require("../middleware/errorHandler");
const logger_1 = require("../utils/logger");
const firebase_1 = require("../config/firebase");
const router = (0, express_1.Router)();
const firestore = (0, firebase_1.getFirestore)();
// Apply authentication to all project routes
router.use(auth_1.authenticateRequest);
/**
 * GET /api/v1/projects
 * List all projects for the authenticated user
 */
router.get('/', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const userId = req.user.uid;
    const tenantId = req.tenantId || 'default';
    const { status, limit = '50', offset = '0' } = req.query;
    logger_1.logger.info('Fetching projects list', {
        userId,
        tenantId,
        status,
        limit,
        offset,
    });
    try {
        // Query Firestore for user's projects
        let projectsRef = firestore
            .collection('projects')
            .where('tenantId', '==', tenantId)
            .where('userId', '==', userId)
            .orderBy('createdAt', 'desc')
            .limit(parseInt(limit));
        if (status) {
            projectsRef = projectsRef.where('status', '==', status);
        }
        const snapshot = await projectsRef.get();
        const projects = snapshot.docs.map((doc) => ({
            id: doc.id,
            ...doc.data(),
        }));
        logger_1.logger.info('Projects fetched successfully', {
            userId,
            count: projects.length,
        });
        res.json({
            success: true,
            data: projects,
            meta: {
                total: projects.length,
                limit: parseInt(limit),
                offset: parseInt(offset),
            },
        });
    }
    catch (error) {
        logger_1.logger.error('Failed to fetch projects', { error, userId });
        throw error;
    }
}));
/**
 * POST /api/v1/projects
 * Create a new project
 */
router.post('/', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const userId = req.user.uid;
    const tenantId = req.tenantId || 'default';
    const { name, description, type, status = 'planning', metadata = {} } = req.body;
    if (!name) {
        return res.status(400).json({
            success: false,
            error: 'Project name is required',
        });
    }
    logger_1.logger.info('Creating new project', {
        userId,
        tenantId,
        name,
        type,
    });
    try {
        const projectData = {
            name,
            description: description || '',
            type: type || 'general',
            status,
            metadata,
            userId,
            tenantId,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            progress: 0,
            priority: 'medium',
            startDate: null,
            endDate: null,
            completedAt: null,
        };
        const projectRef = await firestore.collection('projects').add(projectData);
        const projectId = projectRef.id;
        logger_1.logger.info('Project created successfully', {
            userId,
            projectId,
            name,
        });
        res.status(201).json({
            success: true,
            data: {
                id: projectId,
                ...projectData,
            },
        });
    }
    catch (error) {
        logger_1.logger.error('Failed to create project', { error, userId, name });
        throw error;
    }
}));
/**
 * GET /api/v1/projects/:id
 * Get a specific project by ID
 */
router.get('/:id', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const userId = req.user.uid;
    const tenantId = req.tenantId || 'default';
    const { id } = req.params;
    logger_1.logger.info('Fetching project', { userId, projectId: id });
    try {
        const projectDoc = await firestore.collection('projects').doc(id).get();
        if (!projectDoc.exists) {
            return res.status(404).json({
                success: false,
                error: 'Project not found',
            });
        }
        const projectData = projectDoc.data();
        // Verify user has access to this project
        if (projectData?.userId !== userId && projectData?.tenantId !== tenantId) {
            logger_1.logger.warn('Unauthorized project access attempt', {
                userId,
                projectId: id,
                projectUserId: projectData?.userId,
            });
            return res.status(403).json({
                success: false,
                error: 'Access denied',
            });
        }
        logger_1.logger.info('Project fetched successfully', {
            userId,
            projectId: id,
        });
        res.json({
            success: true,
            data: {
                id: projectDoc.id,
                ...projectData,
            },
        });
    }
    catch (error) {
        logger_1.logger.error('Failed to fetch project', { error, userId, projectId: id });
        throw error;
    }
}));
/**
 * PATCH /api/v1/projects/:id
 * Update a project
 */
router.patch('/:id', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const userId = req.user.uid;
    const tenantId = req.tenantId || 'default';
    const { id } = req.params;
    const updates = req.body;
    logger_1.logger.info('Updating project', {
        userId,
        projectId: id,
        updates: Object.keys(updates),
    });
    try {
        const projectRef = firestore.collection('projects').doc(id);
        const projectDoc = await projectRef.get();
        if (!projectDoc.exists) {
            return res.status(404).json({
                success: false,
                error: 'Project not found',
            });
        }
        const projectData = projectDoc.data();
        // Verify user has access to this project
        if (projectData?.userId !== userId && projectData?.tenantId !== tenantId) {
            logger_1.logger.warn('Unauthorized project update attempt', {
                userId,
                projectId: id,
                projectUserId: projectData?.userId,
            });
            return res.status(403).json({
                success: false,
                error: 'Access denied',
            });
        }
        // Prevent updating protected fields
        delete updates.userId;
        delete updates.tenantId;
        delete updates.createdAt;
        delete updates.id;
        // Add updatedAt timestamp
        updates.updatedAt = new Date().toISOString();
        // If status is being set to 'completed', add completedAt
        if (updates.status === 'completed' && projectData?.status !== 'completed') {
            updates.completedAt = new Date().toISOString();
        }
        await projectRef.update(updates);
        const updatedDoc = await projectRef.get();
        const updatedData = updatedDoc.data();
        logger_1.logger.info('Project updated successfully', {
            userId,
            projectId: id,
        });
        res.json({
            success: true,
            data: {
                id: updatedDoc.id,
                ...updatedData,
            },
        });
    }
    catch (error) {
        logger_1.logger.error('Failed to update project', { error, userId, projectId: id });
        throw error;
    }
}));
/**
 * DELETE /api/v1/projects/:id
 * Delete a project
 */
router.delete('/:id', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const userId = req.user.uid;
    const tenantId = req.tenantId || 'default';
    const { id } = req.params;
    logger_1.logger.info('Deleting project', { userId, projectId: id });
    try {
        const projectRef = firestore.collection('projects').doc(id);
        const projectDoc = await projectRef.get();
        if (!projectDoc.exists) {
            return res.status(404).json({
                success: false,
                error: 'Project not found',
            });
        }
        const projectData = projectDoc.data();
        // Verify user has access to this project
        if (projectData?.userId !== userId && projectData?.tenantId !== tenantId) {
            logger_1.logger.warn('Unauthorized project deletion attempt', {
                userId,
                projectId: id,
                projectUserId: projectData?.userId,
            });
            return res.status(403).json({
                success: false,
                error: 'Access denied',
            });
        }
        await projectRef.delete();
        logger_1.logger.info('Project deleted successfully', {
            userId,
            projectId: id,
        });
        res.json({
            success: true,
            message: 'Project deleted successfully',
        });
    }
    catch (error) {
        logger_1.logger.error('Failed to delete project', { error, userId, projectId: id });
        throw error;
    }
}));
/**
 * GET /api/v1/projects/:id/tasks
 * Get tasks for a project
 */
router.get('/:id/tasks', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const userId = req.user.uid;
    const { id } = req.params;
    const { status, limit = '50' } = req.query;
    logger_1.logger.info('Fetching project tasks', {
        userId,
        projectId: id,
        status,
    });
    try {
        // First verify user has access to the project
        const projectDoc = await firestore.collection('projects').doc(id).get();
        if (!projectDoc.exists) {
            return res.status(404).json({
                success: false,
                error: 'Project not found',
            });
        }
        const projectData = projectDoc.data();
        const tenantId = req.tenantId || 'default';
        if (projectData?.userId !== userId && projectData?.tenantId !== tenantId) {
            return res.status(403).json({
                success: false,
                error: 'Access denied',
            });
        }
        // Query tasks for this project
        let tasksRef = firestore
            .collection('tasks')
            .where('projectId', '==', id)
            .orderBy('createdAt', 'desc')
            .limit(parseInt(limit));
        if (status) {
            tasksRef = tasksRef.where('status', '==', status);
        }
        const snapshot = await tasksRef.get();
        const tasks = snapshot.docs.map((doc) => ({
            id: doc.id,
            ...doc.data(),
        }));
        logger_1.logger.info('Project tasks fetched successfully', {
            userId,
            projectId: id,
            count: tasks.length,
        });
        res.json({
            success: true,
            data: tasks,
            meta: {
                total: tasks.length,
                projectId: id,
            },
        });
    }
    catch (error) {
        logger_1.logger.error('Failed to fetch project tasks', {
            error,
            userId,
            projectId: id,
        });
        throw error;
    }
}));
/**
 * POST /api/v1/projects/:id/tasks
 * Create a task for a project
 */
router.post('/:id/tasks', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const userId = req.user.uid;
    const { id } = req.params;
    const { title, description, status = 'todo', priority = 'medium', dueDate } = req.body;
    if (!title) {
        return res.status(400).json({
            success: false,
            error: 'Task title is required',
        });
    }
    logger_1.logger.info('Creating project task', {
        userId,
        projectId: id,
        title,
    });
    try {
        // Verify user has access to the project
        const projectDoc = await firestore.collection('projects').doc(id).get();
        if (!projectDoc.exists) {
            return res.status(404).json({
                success: false,
                error: 'Project not found',
            });
        }
        const projectData = projectDoc.data();
        const tenantId = req.tenantId || 'default';
        if (projectData?.userId !== userId && projectData?.tenantId !== tenantId) {
            return res.status(403).json({
                success: false,
                error: 'Access denied',
            });
        }
        const taskData = {
            title,
            description: description || '',
            status,
            priority,
            dueDate: dueDate || null,
            projectId: id,
            userId,
            tenantId,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            completedAt: null,
        };
        const taskRef = await firestore.collection('tasks').add(taskData);
        const taskId = taskRef.id;
        logger_1.logger.info('Project task created successfully', {
            userId,
            projectId: id,
            taskId,
        });
        res.status(201).json({
            success: true,
            data: {
                id: taskId,
                ...taskData,
            },
        });
    }
    catch (error) {
        logger_1.logger.error('Failed to create project task', {
            error,
            userId,
            projectId: id,
        });
        throw error;
    }
}));
exports.default = router;
//# sourceMappingURL=projects.js.map