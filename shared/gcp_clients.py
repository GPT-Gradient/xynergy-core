"""
Shared GCP Client Manager for Connection Pooling
Optimizes resource usage across all services by providing reusable client instances.
"""
import threading
from typing import Optional
from google.cloud import firestore, pubsub_v1, storage, bigquery
import logging

logger = logging.getLogger(__name__)

class GCPClientManager:
    """Centralized manager for GCP client connections with connection pooling."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._firestore_client: Optional[firestore.Client] = None
            self._bigquery_client: Optional[bigquery.Client] = None
            self._storage_client: Optional[storage.Client] = None
            self._publisher_client: Optional[pubsub_v1.PublisherClient] = None
            self._subscriber_client: Optional[pubsub_v1.SubscriberClient] = None
            self._client_lock = threading.Lock()
            self._initialized = True

    def get_firestore_client(self) -> firestore.Client:
        """Get or create Firestore client with connection pooling."""
        if self._firestore_client is None:
            with self._client_lock:
                if self._firestore_client is None:
                    try:
                        self._firestore_client = firestore.Client()
                        logger.info("Created new Firestore client")
                    except Exception as e:
                        logger.error(f"Failed to create Firestore client: {e}")
                        raise
        return self._firestore_client

    def get_bigquery_client(self) -> bigquery.Client:
        """Get or create BigQuery client with connection pooling."""
        if self._bigquery_client is None:
            with self._client_lock:
                if self._bigquery_client is None:
                    try:
                        self._bigquery_client = bigquery.Client()
                        logger.info("Created new BigQuery client")
                    except Exception as e:
                        logger.error(f"Failed to create BigQuery client: {e}")
                        raise
        return self._bigquery_client

    def get_storage_client(self) -> storage.Client:
        """Get or create Cloud Storage client with connection pooling."""
        if self._storage_client is None:
            with self._client_lock:
                if self._storage_client is None:
                    try:
                        self._storage_client = storage.Client()
                        logger.info("Created new Storage client")
                    except Exception as e:
                        logger.error(f"Failed to create Storage client: {e}")
                        raise
        return self._storage_client

    def get_publisher_client(self) -> pubsub_v1.PublisherClient:
        """Get or create Pub/Sub Publisher client with connection pooling."""
        if self._publisher_client is None:
            with self._client_lock:
                if self._publisher_client is None:
                    try:
                        self._publisher_client = pubsub_v1.PublisherClient()
                        logger.info("Created new Publisher client")
                    except Exception as e:
                        logger.error(f"Failed to create Publisher client: {e}")
                        raise
        return self._publisher_client

    def get_subscriber_client(self) -> pubsub_v1.SubscriberClient:
        """Get or create Pub/Sub Subscriber client with connection pooling."""
        if self._subscriber_client is None:
            with self._client_lock:
                if self._subscriber_client is None:
                    try:
                        self._subscriber_client = pubsub_v1.SubscriberClient()
                        logger.info("Created new Subscriber client")
                    except Exception as e:
                        logger.error(f"Failed to create Subscriber client: {e}")
                        raise
        return self._subscriber_client

    def close_all_connections(self):
        """Close all client connections for clean shutdown."""
        with self._client_lock:
            try:
                if self._firestore_client:
                    self._firestore_client.close()
                    self._firestore_client = None
                    logger.info("Closed Firestore client")

                if self._publisher_client:
                    # Publisher client doesn't have close method, but we can reset the reference
                    self._publisher_client = None
                    logger.info("Reset Publisher client")

                if self._subscriber_client:
                    # Subscriber client doesn't have close method, but we can reset the reference
                    self._subscriber_client = None
                    logger.info("Reset Subscriber client")

                if self._bigquery_client:
                    self._bigquery_client.close()
                    self._bigquery_client = None
                    logger.info("Closed BigQuery client")

                if self._storage_client:
                    # Storage client doesn't have close method, but we can reset the reference
                    self._storage_client = None
                    logger.info("Reset Storage client")

            except Exception as e:
                logger.error(f"Error during client cleanup: {e}")

# Global instance for easy importing
gcp_clients = GCPClientManager()

# Convenience functions for backward compatibility
def get_firestore_client() -> firestore.Client:
    """Convenience function to get Firestore client."""
    return gcp_clients.get_firestore_client()

def get_bigquery_client() -> bigquery.Client:
    """Convenience function to get BigQuery client."""
    return gcp_clients.get_bigquery_client()

def get_storage_client() -> storage.Client:
    """Convenience function to get Storage client."""
    return gcp_clients.get_storage_client()

def get_publisher_client() -> pubsub_v1.PublisherClient:
    """Convenience function to get Publisher client."""
    return gcp_clients.get_publisher_client()

def get_subscriber_client() -> pubsub_v1.SubscriberClient:
    """Convenience function to get Subscriber client."""
    return gcp_clients.get_subscriber_client()