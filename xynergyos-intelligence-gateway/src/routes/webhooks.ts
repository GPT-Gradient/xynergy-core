import { Router, Request, Response } from 'express';
import { asyncHandler } from '../middleware/errorHandler';
import { logger } from '../utils/logger';
import * as crypto from 'crypto';
import { PubSub } from '@google-cloud/pubsub';

const router = Router();
const pubsub = new PubSub();

/**
 * Webhook Handlers for Real-Time Events
 *
 * Supported webhooks:
 * - Slack Events API
 * - Gmail Push Notifications (Pub/Sub)
 * - Calendar Events (Pub/Sub)
 */

/**
 * Slack Events API Webhook
 *
 * Handles real-time events from Slack workspace
 */
router.post(
  '/slack/events',
  asyncHandler(async (req: Request, res: Response) => {
    const slackSignature = req.headers['x-slack-signature'] as string;
    const slackTimestamp = req.headers['x-slack-request-timestamp'] as string;
    const signingSecret = process.env.SLACK_SIGNING_SECRET;

    // Verify Slack signature
    if (signingSecret) {
      const isValid = verifySlackSignature(
        signingSecret,
        req.body,
        slackTimestamp,
        slackSignature
      );

      if (!isValid) {
        logger.warn('Invalid Slack signature');
        return res.status(401).json({ error: 'Invalid signature' });
      }
    }

    const event = req.body;

    // Handle URL verification challenge
    if (event.type === 'url_verification') {
      logger.info('Slack URL verification');
      return res.json({ challenge: event.challenge });
    }

    // Handle event callback
    if (event.type === 'event_callback') {
      const slackEvent = event.event;

      logger.info('Slack event received', {
        type: slackEvent.type,
        user: slackEvent.user,
        channel: slackEvent.channel,
      });

      // Publish to Pub/Sub for async processing
      await publishToPubSub('slack-events', {
        eventType: slackEvent.type,
        event: slackEvent,
        teamId: event.team_id,
        apiAppId: event.api_app_id,
        timestamp: new Date().toISOString(),
      });

      // Acknowledge receipt immediately
      res.json({ ok: true });

      // Process event asynchronously
      await handleSlackEvent(slackEvent);
    } else {
      res.json({ ok: true });
    }
  })
);

/**
 * Slack Interactivity Webhook
 *
 * Handles button clicks, menu selections, etc.
 */
router.post(
  '/slack/interactive',
  asyncHandler(async (req: Request, res: Response) => {
    const payload = JSON.parse(req.body.payload);

    logger.info('Slack interactive event', {
      type: payload.type,
      actionId: payload.actions?.[0]?.action_id,
      user: payload.user?.id,
    });

    // Acknowledge immediately
    res.json({ ok: true });

    // Process interaction asynchronously
    await handleSlackInteraction(payload);
  })
);

/**
 * Gmail Push Notification Webhook
 *
 * Handles Gmail watch notifications via Pub/Sub
 */
router.post(
  '/gmail/push',
  asyncHandler(async (req: Request, res: Response) => {
    // Gmail sends notifications via Pub/Sub
    const message = req.body.message;

    if (!message || !message.data) {
      logger.warn('Invalid Gmail push notification');
      return res.status(400).json({ error: 'Invalid notification' });
    }

    // Decode the message
    const data = JSON.parse(Buffer.from(message.data, 'base64').toString());

    logger.info('Gmail push notification', {
      emailAddress: data.emailAddress,
      historyId: data.historyId,
    });

    // Acknowledge immediately
    res.json({ ok: true });

    // Process notification asynchronously
    await handleGmailNotification(data);
  })
);

/**
 * Calendar Push Notification Webhook
 *
 * Handles Calendar event changes via Pub/Sub
 */
router.post(
  '/calendar/push',
  asyncHandler(async (req: Request, res: Response) => {
    const message = req.body.message;

    if (!message || !message.data) {
      logger.warn('Invalid Calendar push notification');
      return res.status(400).json({ error: 'Invalid notification' });
    }

    // Decode the message
    const data = JSON.parse(Buffer.from(message.data, 'base64').toString());

    logger.info('Calendar push notification', {
      calendarId: data.calendarId,
      resourceId: data.resourceId,
    });

    // Acknowledge immediately
    res.json({ ok: true });

    // Process notification asynchronously
    await handleCalendarNotification(data);
  })
);

/**
 * Generic Webhook Health Check
 */
router.get(
  '/health',
  asyncHandler(async (req: Request, res: Response) => {
    res.json({
      status: 'healthy',
      webhooks: {
        slack: 'active',
        gmail: 'active',
        calendar: 'active',
      },
      timestamp: new Date().toISOString(),
    });
  })
);

/**
 * Helper Functions
 */

/**
 * Verify Slack request signature
 */
function verifySlackSignature(
  signingSecret: string,
  body: any,
  timestamp: string,
  signature: string
): boolean {
  // Check timestamp to prevent replay attacks
  const time = Math.floor(Date.now() / 1000);
  if (Math.abs(time - parseInt(timestamp)) > 60 * 5) {
    // Request is older than 5 minutes
    return false;
  }

  const hmac = crypto.createHmac('sha256', signingSecret);
  const sigBasestring = `v0:${timestamp}:${JSON.stringify(body)}`;
  hmac.update(sigBasestring);
  const mySignature = `v0=${hmac.digest('hex')}`;

  return crypto.timingSafeEqual(
    Buffer.from(mySignature),
    Buffer.from(signature)
  );
}

/**
 * Publish event to Pub/Sub
 */
async function publishToPubSub(topicName: string, data: any): Promise<void> {
  try {
    const topic = pubsub.topic(topicName);
    const dataBuffer = Buffer.from(JSON.stringify(data));
    await topic.publishMessage({ data: dataBuffer });

    logger.info('Event published to Pub/Sub', { topic: topicName });
  } catch (error) {
    logger.error('Failed to publish to Pub/Sub', { error, topic: topicName });
  }
}

/**
 * Handle Slack Event
 */
async function handleSlackEvent(event: any): Promise<void> {
  switch (event.type) {
    case 'message':
      await handleSlackMessage(event);
      break;

    case 'channel_created':
      logger.info('New Slack channel created', {
        channelId: event.channel?.id,
        channelName: event.channel?.name,
      });
      break;

    case 'member_joined_channel':
      logger.info('Member joined Slack channel', {
        userId: event.user,
        channelId: event.channel,
      });
      break;

    case 'app_mention':
      await handleSlackMention(event);
      break;

    default:
      logger.info('Unhandled Slack event', { type: event.type });
  }
}

/**
 * Handle Slack Message
 */
async function handleSlackMessage(event: any): Promise<void> {
  // Ignore bot messages to prevent loops
  if (event.bot_id) {
    return;
  }

  logger.info('Slack message received', {
    channel: event.channel,
    user: event.user,
    text: event.text?.substring(0, 50),
  });

  // Process message for:
  // - AI analysis
  // - Sentiment tracking
  // - Action items extraction
  // - Context building for meeting prep
}

/**
 * Handle Slack Mention
 */
async function handleSlackMention(event: any): Promise<void> {
  logger.info('Bot mentioned in Slack', {
    channel: event.channel,
    user: event.user,
    text: event.text,
  });

  // Respond to mentions:
  // - Answer questions
  // - Provide summaries
  // - Execute commands
}

/**
 * Handle Slack Interaction
 */
async function handleSlackInteraction(payload: any): Promise<void> {
  logger.info('Slack interaction processed', {
    type: payload.type,
    callbackId: payload.callback_id,
  });

  // Handle:
  // - Button clicks
  // - Menu selections
  // - Modal submissions
  // - Shortcuts
}

/**
 * Handle Gmail Notification
 */
async function handleGmailNotification(data: any): Promise<void> {
  logger.info('Gmail notification processed', {
    emailAddress: data.emailAddress,
    historyId: data.historyId,
  });

  // Fetch new/modified messages using historyId
  // Process for:
  // - Important email detection
  // - Action item extraction
  // - Calendar event suggestions
  // - Auto-response triggers
}

/**
 * Handle Calendar Notification
 */
async function handleCalendarNotification(data: any): Promise<void> {
  logger.info('Calendar notification processed', {
    calendarId: data.calendarId,
    resourceId: data.resourceId,
  });

  // Fetch changed events
  // Process for:
  // - Meeting prep updates
  // - Conflict detection
  // - Reminder scheduling
  // - Attendee coordination
}

export default router;
