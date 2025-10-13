import { Router, Request, Response } from 'express';
import { Firestore } from '@google-cloud/firestore';
import { asyncHandler } from '../middleware/errorHandler';
import { logger } from '../utils/logger';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';
import { v4 as uuidv4 } from 'uuid';

const router = Router();
const firestore = new Firestore();

/**
 * Authentication Routes
 *
 * Provides JWT-based authentication for the frontend
 * Stores user credentials in Firestore
 */

interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

interface LoginRequest {
  username: string;
  password: string;
}

/**
 * POST /api/v1/auth/register
 *
 * Register a new user
 */
router.post(
  '/register',
  asyncHandler(async (req: Request, res: Response) => {
    const { email, username, password, full_name }: RegisterRequest = req.body;

    // Validation
    if (!email || !username || !password) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: email, username, password',
      });
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid email format',
      });
    }

    // Password strength validation
    if (password.length < 8) {
      return res.status(400).json({
        success: false,
        error: 'Password must be at least 8 characters',
      });
    }

    try {
      // Check if user already exists
      const usersRef = firestore.collection('users');

      const emailCheck = await usersRef.where('email', '==', email).limit(1).get();
      if (!emailCheck.empty) {
        return res.status(409).json({
          success: false,
          error: 'Email already registered',
        });
      }

      const usernameCheck = await usersRef.where('username', '==', username).limit(1).get();
      if (!usernameCheck.empty) {
        return res.status(409).json({
          success: false,
          error: 'Username already taken',
        });
      }

      // Hash password
      const saltRounds = 10;
      const passwordHash = await bcrypt.hash(password, saltRounds);

      // Create user
      const userId = uuidv4();
      const tenantId = 'clearforge'; // Default tenant

      const userData = {
        userId,
        email,
        username,
        passwordHash,
        fullName: full_name || username,
        tenantId,
        roles: ['user'],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        isActive: true,
      };

      await usersRef.doc(userId).set(userData);

      logger.info('User registered successfully', {
        userId,
        email,
        username,
      });

      // Generate JWT token
      const token = generateToken({
        user_id: userId,
        tenant_id: tenantId,
        email,
        username,
        roles: ['user'],
      });

      res.status(201).json({
        success: true,
        access_token: token,
        token_type: 'Bearer',
        expires_in: 86400, // 24 hours
        user: {
          userId,
          email,
          username,
          fullName: userData.fullName,
          roles: ['user'],
        },
      });
    } catch (error) {
      logger.error('Registration failed', { error, email, username });
      res.status(500).json({
        success: false,
        error: 'Registration failed. Please try again.',
      });
    }
  })
);

/**
 * POST /api/v1/auth/login
 *
 * Login with username/email and password
 * Accepts form data or JSON
 */
router.post(
  '/login',
  asyncHandler(async (req: Request, res: Response) => {
    // Support both form data and JSON
    const username = req.body.username || req.body.get?.('username');
    const password = req.body.password || req.body.get?.('password');

    if (!username || !password) {
      return res.status(400).json({
        success: false,
        error: 'Missing username or password',
      });
    }

    try {
      // Find user by username or email
      const usersRef = firestore.collection('users');

      let userDoc;
      const usernameQuery = await usersRef.where('username', '==', username).limit(1).get();

      if (!usernameQuery.empty) {
        userDoc = usernameQuery.docs[0];
      } else {
        // Try email
        const emailQuery = await usersRef.where('email', '==', username).limit(1).get();
        if (!emailQuery.empty) {
          userDoc = emailQuery.docs[0];
        }
      }

      if (!userDoc) {
        logger.warn('Login attempt with invalid username', { username });
        return res.status(401).json({
          success: false,
          error: 'Invalid username or password',
        });
      }

      const userData = userDoc.data();

      // Check if account is active
      if (!userData.isActive) {
        return res.status(403).json({
          success: false,
          error: 'Account is disabled. Please contact support.',
        });
      }

      // Verify password
      const isPasswordValid = await bcrypt.compare(password, userData.passwordHash);

      if (!isPasswordValid) {
        logger.warn('Login attempt with invalid password', {
          userId: userData.userId,
          username,
        });
        return res.status(401).json({
          success: false,
          error: 'Invalid username or password',
        });
      }

      // Update last login
      await userDoc.ref.update({
        lastLoginAt: new Date().toISOString(),
      });

      logger.info('User logged in successfully', {
        userId: userData.userId,
        username: userData.username,
      });

      // Generate JWT token
      const token = generateToken({
        user_id: userData.userId,
        tenant_id: userData.tenantId || 'clearforge',
        email: userData.email,
        username: userData.username,
        roles: userData.roles || ['user'],
      });

      res.json({
        success: true,
        access_token: token,
        token_type: 'Bearer',
        expires_in: 86400, // 24 hours
        user: {
          userId: userData.userId,
          email: userData.email,
          username: userData.username,
          fullName: userData.fullName,
          roles: userData.roles || ['user'],
        },
      });
    } catch (error) {
      logger.error('Login failed', { error, username });
      res.status(500).json({
        success: false,
        error: 'Login failed. Please try again.',
      });
    }
  })
);

/**
 * POST /api/v1/auth/refresh
 *
 * Refresh JWT token (optional - for future use)
 */
router.post(
  '/refresh',
  asyncHandler(async (req: Request, res: Response) => {
    const { refresh_token } = req.body;

    if (!refresh_token) {
      return res.status(400).json({
        success: false,
        error: 'Refresh token required',
      });
    }

    // TODO: Implement refresh token logic with separate refresh token storage
    // For now, return error
    res.status(501).json({
      success: false,
      error: 'Token refresh not yet implemented. Please login again.',
    });
  })
);

/**
 * POST /api/v1/auth/logout
 *
 * Logout (optional - mainly for cleanup)
 */
router.post(
  '/logout',
  asyncHandler(async (req: Request, res: Response) => {
    // With JWT, logout is handled client-side by removing the token
    // Server-side logout would require token blacklisting (future enhancement)

    logger.info('User logged out', {
      userId: (req as any).user?.uid,
    });

    res.json({
      success: true,
      message: 'Logged out successfully',
    });
  })
);

/**
 * Helper: Generate JWT token
 */
function generateToken(payload: {
  user_id: string;
  tenant_id: string;
  email: string;
  username: string;
  roles: string[];
}): string {
  const jwtSecret = process.env.JWT_SECRET;

  if (!jwtSecret) {
    throw new Error('JWT_SECRET not configured');
  }

  return jwt.sign(payload, jwtSecret, {
    expiresIn: '24h',
    issuer: 'xynergyos-intelligence-gateway',
    subject: payload.user_id,
  });
}

export default router;
