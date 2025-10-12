/**
 * Pub/Sub Event Publisher
 */

import { PubSub } from '@google-cloud/pubsub';
import { logger } from './logger';
import { EntityEvent } from '../types';

class PubSubPublisher {
  private pubsub: PubSub;
  private topicName = 'xynergy-entity-events';

  constructor() {
    this.pubsub = new PubSub({
      projectId: process.env.PROJECT_ID || 'xynergy-dev-1757909467',
    });
  }

  /**
   * Publish entity event
   */
  async publishEntityEvent(event: EntityEvent): Promise<void> {
    try {
      const topic = this.pubsub.topic(this.topicName);
      const messageData = Buffer.from(JSON.stringify(event));

      const messageId = await topic.publishMessage({
        data: messageData,
        attributes: {
          eventType: event.eventType,
          entityId: event.entityId,
          timestamp: event.timestamp,
        },
      });

      logger.info('Entity event published', {
        messageId,
        eventType: event.eventType,
        entityId: event.entityId,
      });
    } catch (error) {
      logger.error('Failed to publish entity event', {
        error,
        eventType: event.eventType,
        entityId: event.entityId,
      });
      // Don't throw - event publishing failure shouldn't block the operation
    }
  }
}

export const pubsubPublisher = new PubSubPublisher();
