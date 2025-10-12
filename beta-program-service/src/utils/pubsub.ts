/**
 * Pub/Sub Event Publisher for Beta Events
 */

import { PubSub } from '@google-cloud/pubsub';
import { logger } from './logger';
import { BetaEvent } from '../types';

class PubSubPublisher {
  private pubsub: PubSub;
  private topicName = 'xynergy-beta-events';

  constructor() {
    this.pubsub = new PubSub({
      projectId: process.env.PROJECT_ID || 'xynergy-dev-1757909467',
    });
  }

  /**
   * Publish beta event
   */
  async publishBetaEvent(event: BetaEvent): Promise<void> {
    try {
      const topic = this.pubsub.topic(this.topicName);
      const messageData = Buffer.from(JSON.stringify(event));

      const messageId = await topic.publishMessage({
        data: messageData,
        attributes: {
          eventType: event.eventType,
          timestamp: event.timestamp,
          ...(event.userId && { userId: event.userId }),
          ...(event.phase && { phase: event.phase }),
        },
      });

      logger.info('Beta event published', {
        messageId,
        eventType: event.eventType,
        userId: event.userId,
      });
    } catch (error) {
      logger.error('Failed to publish beta event', {
        error,
        eventType: event.eventType,
      });
      // Don't throw - event publishing failure shouldn't block the operation
    }
  }
}

export const pubsubPublisher = new PubSubPublisher();
