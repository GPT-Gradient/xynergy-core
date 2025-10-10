"""
Simple Cache Utility
In-memory cache with TTL support. Can be replaced with Redis in production.
"""

import time
from typing import Any, Optional, Dict
import structlog

logger = structlog.get_logger()


class SimpleCache:
    """
    Simple in-memory cache with TTL support

    Stores data in memory with automatic expiration.
    Thread-safe for single-process applications.
    For multi-instance deployments, use Redis instead.
    """

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "evictions": 0
        }

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        if key not in self._cache:
            self._stats["misses"] += 1
            return None

        entry = self._cache[key]
        expires_at = entry.get("expires_at")

        # Check if expired
        if expires_at and time.time() > expires_at:
            del self._cache[key]
            self._stats["evictions"] += 1
            self._stats["misses"] += 1
            return None

        self._stats["hits"] += 1
        return entry.get("value")

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (default: 300 = 5 minutes)
        """
        expires_at = time.time() + ttl if ttl > 0 else None

        self._cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": time.time()
        }

        self._stats["sets"] += 1

        # Cleanup old entries periodically (every 100 sets)
        if self._stats["sets"] % 100 == 0:
            self._cleanup_expired()

    def delete(self, key: str) -> bool:
        """
        Delete key from cache

        Args:
            key: Cache key

        Returns:
            True if key existed and was deleted, False otherwise
        """
        if key in self._cache:
            del self._cache[key]
            self._stats["deletes"] += 1
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries"""
        count = len(self._cache)
        self._cache.clear()
        logger.info("cache_cleared", entries_removed=count)

    def _cleanup_expired(self) -> None:
        """Remove expired entries from cache"""
        current_time = time.time()
        keys_to_delete = []

        for key, entry in self._cache.items():
            expires_at = entry.get("expires_at")
            if expires_at and current_time > expires_at:
                keys_to_delete.append(key)

        for key in keys_to_delete:
            del self._cache[key]
            self._stats["evictions"] += 1

        if keys_to_delete:
            logger.info("cache_cleanup", evicted=len(keys_to_delete))

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            **self._stats,
            "entries": len(self._cache),
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": total_requests
        }

    def size(self) -> int:
        """Return number of entries in cache"""
        return len(self._cache)
