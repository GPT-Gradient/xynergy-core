"""
Consolidated Pub/Sub Management for Xynergy Platform
Optimizes message routing and reduces topic overhead through intelligent consolidation.
"""
import os
import json
import asyncio
import threading
from typing import Dict, Any, List, Callable, Optional
from google.cloud import pubsub_v1
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PubSubManager:
    """Centralized Pub/Sub manager with topic consolidation and intelligent routing."""

    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        self._subscribers = {}
        self._message_handlers = {}
        self._lock = threading.Lock()

        # Consolidated topic mapping
        self.topic_consolidation_map = {
            # AI Services -> single ai-platform-events topic
            "ai-routing-engine-events": "ai-platform-events",
            "ai-providers-events": "ai-platform-events",
            "internal-ai-service-events": "ai-platform-events",
            "ai-assistant-events": "ai-platform-events",

            # Analytics & Data -> single analytics-events topic
            "analytics-data-layer-events": "analytics-events",
            "advanced-analytics-events": "analytics-events",
            "executive-dashboard-events": "analytics-events",
            "keyword-revenue-tracker-events": "analytics-events",
            "attribution-coordinator-events": "analytics-events",

            # Content & Marketing -> single content-platform-events topic
            "marketing-engine-events": "content-platform-events",
            "content-hub-events": "content-platform-events",
            "rapid-content-generator-events": "content-platform-events",

            # System & Security -> single platform-system-events topic
            "system-runtime-events": "platform-system-events",
            "security-governance-events": "platform-system-events",
            "tenant-management-events": "platform-system-events",
            "secrets-config-events": "platform-system-events",

            # Workflow & Automation -> single workflow-events topic
            "scheduler-automation-engine-events": "workflow-events",
            "ai-workflow-engine-events": "workflow-events",
            "validation-coordinator-events": "workflow-events",

            # Research & Trending -> single intelligence-events topic
            "research-coordinator-events": "intelligence-events",
            "trending-engine-coordinator-events": "intelligence-events",
            "market-intelligence-service-events": "intelligence-events",
            "competitive-analysis-service-events": "intelligence-events",

            # Quality & Compliance -> single quality-events topic
            "qa-engine-events": "quality-events",
            "trust-safety-validator-events": "quality-events",
            "plagiarism-detector-events": "quality-events",
            "fact-checking-service-events": "quality-events"
        }

        # Consolidated topics (6 instead of 25+)
        self.consolidated_topics = [
            "ai-platform-events",
            "analytics-events",
            "content-platform-events",
            "platform-system-events",
            "workflow-events",
            "intelligence-events",
            "quality-events"
        ]

    def get_consolidated_topic(self, original_topic: str) -> str:
        """Get the consolidated topic for an original service topic."""
        return self.topic_consolidation_map.get(original_topic, original_topic)

    def publish_message(self, topic_name: str, message_data: Dict[str, Any],
                       service_name: str = None, message_type: str = "event") -> str:
        """Publish message to appropriate consolidated topic."""
        try:
            # Use consolidated topic
            consolidated_topic = self.get_consolidated_topic(topic_name)
            topic_path = self.publisher.topic_path(self.project_id, consolidated_topic)

            # Enrich message with routing metadata
            enriched_message = {
                "original_topic": topic_name,
                "consolidated_topic": consolidated_topic,
                "service_name": service_name or "unknown",
                "message_type": message_type,
                "timestamp": datetime.now().isoformat(),
                "data": message_data
            }

            # Serialize and publish
            message_json = json.dumps(enriched_message).encode("utf-8")

            # Add routing attributes for filtering
            attributes = {
                "service": service_name or "unknown",
                "type": message_type,
                "original_topic": topic_name
            }

            future = self.publisher.publish(topic_path, message_json, **attributes)
            message_id = future.result()

            logger.debug(f"Published message {message_id} to {consolidated_topic} from {service_name}")
            return message_id

        except Exception as e:
            logger.error(f"Failed to publish message to {topic_name}: {e}")
            raise

    def subscribe_to_messages(self, topic_name: str, handler: Callable[[Dict[str, Any]], None],
                            service_filter: str = None, message_type_filter: str = None):
        """Subscribe to messages from consolidated topics with filtering."""
        try:
            consolidated_topic = self.get_consolidated_topic(topic_name)
            subscription_name = f"{topic_name}-subscription"
            subscription_path = self.subscriber.subscription_path(self.project_id, subscription_name)

            def message_callback(message):
                try:
                    # Parse message
                    message_data = json.loads(message.data.decode("utf-8"))

                    # Apply filters
                    if service_filter and message_data.get("service_name") != service_filter:
                        message.ack()
                        return

                    if message_type_filter and message_data.get("message_type") != message_type_filter:
                        message.ack()
                        return

                    # Only process if original topic matches (for backwards compatibility)
                    if message_data.get("original_topic") == topic_name:
                        handler(message_data.get("data", {}))

                    message.ack()

                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    message.nack()

            # Start subscription
            with self._lock:
                if subscription_name not in self._subscribers:
                    flow_control = pubsub_v1.types.FlowControl(max_messages=100, max_bytes=1024*1024*10)
                    self._subscribers[subscription_name] = self.subscriber.subscribe(
                        subscription_path, callback=message_callback, flow_control=flow_control
                    )
                    logger.info(f"Started subscription to {consolidated_topic} for {topic_name}")

        except Exception as e:
            logger.error(f"Failed to subscribe to {topic_name}: {e}")
            raise

    def create_consolidated_topics(self) -> Dict[str, bool]:
        """Create all consolidated topics if they don't exist."""
        results = {}

        for topic_name in self.consolidated_topics:
            try:
                topic_path = self.publisher.topic_path(self.project_id, topic_name)

                try:
                    self.publisher.create_topic(request={"name": topic_path})
                    results[topic_name] = True
                    logger.info(f"Created consolidated topic: {topic_name}")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        results[topic_name] = True
                        logger.debug(f"Topic {topic_name} already exists")
                    else:
                        raise

            except Exception as e:
                logger.error(f"Failed to create topic {topic_name}: {e}")
                results[topic_name] = False

        return results

    def create_consolidated_subscriptions(self) -> Dict[str, bool]:
        """Create subscriptions for all consolidated topics."""
        results = {}

        for topic_name in self.consolidated_topics:
            try:
                topic_path = self.publisher.topic_path(self.project_id, topic_name)
                subscription_name = f"{topic_name}-consolidated-sub"
                subscription_path = self.subscriber.subscription_path(self.project_id, subscription_name)

                try:
                    self.subscriber.create_subscription(
                        request={
                            "name": subscription_path,
                            "topic": topic_path,
                            "ack_deadline_seconds": 60,
                            "message_retention_duration": {"seconds": 604800}  # 7 days
                        }
                    )
                    results[subscription_name] = True
                    logger.info(f"Created subscription: {subscription_name}")

                except Exception as e:
                    if "already exists" in str(e).lower():
                        results[subscription_name] = True
                        logger.debug(f"Subscription {subscription_name} already exists")
                    else:
                        raise

            except Exception as e:
                logger.error(f"Failed to create subscription for {topic_name}: {e}")
                results[f"{topic_name}-sub"] = False

        return results

    def get_topic_metrics(self) -> Dict[str, Any]:
        """Get metrics for all consolidated topics."""
        metrics = {}

        try:
            for topic_name in self.consolidated_topics:
                topic_path = self.publisher.topic_path(self.project_id, topic_name)

                # Get topic info
                try:
                    topic = self.publisher.get_topic(request={"topic": topic_path})

                    # Get subscriptions for this topic
                    subscriptions = list(self.publisher.list_topic_subscriptions(
                        request={"topic": topic_path}
                    ))

                    metrics[topic_name] = {
                        "topic_path": topic_path,
                        "subscription_count": len(subscriptions),
                        "subscriptions": subscriptions,
                        "created": True
                    }

                except Exception as e:
                    metrics[topic_name] = {
                        "topic_path": topic_path,
                        "created": False,
                        "error": str(e)
                    }

        except Exception as e:
            logger.error(f"Failed to get topic metrics: {e}")

        return metrics

    def cleanup_old_topics(self, dry_run: bool = True) -> Dict[str, Any]:
        """Clean up old individual service topics (use with caution)."""
        cleanup_results = {
            "topics_to_delete": [],
            "subscriptions_to_delete": [],
            "dry_run": dry_run,
            "deleted_topics": [],
            "deleted_subscriptions": [],
            "errors": []
        }

        try:
            # List all topics
            project_path = f"projects/{self.project_id}"
            topics = list(self.publisher.list_topics(request={"project": project_path}))

            for topic in topics:
                topic_name = topic.name.split("/")[-1]

                # Check if this is an old topic that should be consolidated
                if topic_name in self.topic_consolidation_map:
                    cleanup_results["topics_to_delete"].append(topic_name)

                    if not dry_run:
                        try:
                            # Delete subscriptions first
                            subscriptions = list(self.publisher.list_topic_subscriptions(
                                request={"topic": topic.name}
                            ))

                            for sub in subscriptions:
                                self.subscriber.delete_subscription(request={"subscription": sub})
                                cleanup_results["deleted_subscriptions"].append(sub)

                            # Delete topic
                            self.publisher.delete_topic(request={"topic": topic.name})
                            cleanup_results["deleted_topics"].append(topic_name)

                        except Exception as e:
                            cleanup_results["errors"].append(f"Failed to delete {topic_name}: {str(e)}")

        except Exception as e:
            cleanup_results["errors"].append(f"Failed to list topics: {str(e)}")

        return cleanup_results

    def close(self):
        """Close all subscribers and connections."""
        with self._lock:
            for subscription_name, subscriber_future in self._subscribers.items():
                try:
                    subscriber_future.cancel()
                    logger.info(f"Cancelled subscription: {subscription_name}")
                except Exception as e:
                    logger.error(f"Error cancelling subscription {subscription_name}: {e}")

            self._subscribers.clear()

# Global instance for easy importing
pubsub_manager = PubSubManager()

# Convenience functions
def publish_event(topic_name: str, event_data: Dict[str, Any], service_name: str = None) -> str:
    """Convenience function to publish events."""
    return pubsub_manager.publish_message(topic_name, event_data, service_name, "event")

def publish_notification(topic_name: str, notification_data: Dict[str, Any], service_name: str = None) -> str:
    """Convenience function to publish notifications."""
    return pubsub_manager.publish_message(topic_name, notification_data, service_name, "notification")

def subscribe_to_events(topic_name: str, handler: Callable[[Dict[str, Any]], None],
                       service_filter: str = None):
    """Convenience function to subscribe to events."""
    return pubsub_manager.subscribe_to_messages(topic_name, handler, service_filter, "event")

def setup_consolidated_pubsub() -> Dict[str, Any]:
    """Set up all consolidated Pub/Sub infrastructure."""
    return {
        "topics_created": pubsub_manager.create_consolidated_topics(),
        "subscriptions_created": pubsub_manager.create_consolidated_subscriptions(),
        "metrics": pubsub_manager.get_topic_metrics()
    }