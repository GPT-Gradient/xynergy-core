"""
Redis Cache Manager for Xynergy Platform
Implements intelligent caching for AI responses and frequently accessed data.
"""
import os
import json
import hashlib
import asyncio
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta
import redis.asyncio as redis
import logging

logger = logging.getLogger(__name__)

class RedisCache:
    """Centralized Redis cache manager with intelligent caching strategies."""

    def __init__(self, redis_host: str = None, redis_port: int = 6379, redis_db: int = 0):
        self.redis_host = redis_host or os.getenv("REDIS_HOST", "10.0.0.3")  # Default from terraform
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.client: Optional[redis.Redis] = None
        self._connected = False

        # Cache TTL configurations (in seconds)
        self.cache_ttl_config = {
            "ai_responses": 3600,           # 1 hour
            "api_responses": 1800,          # 30 minutes
            "user_sessions": 7200,          # 2 hours
            "analytics_data": 900,          # 15 minutes
            "content_metadata": 1800,       # 30 minutes
            "system_health": 300,           # 5 minutes
            "expensive_queries": 3600,      # 1 hour
            "trending_data": 300,           # 5 minutes (frequent updates)
        }

        # Cache key prefixes
        self.key_prefixes = {
            "ai_response": "ai:resp:",
            "api_call": "api:call:",
            "user_session": "user:sess:",
            "analytics": "analytics:",
            "content": "content:",
            "system": "system:",
            "query": "query:",
            "trend": "trend:"
        }

    async def connect(self):
        """Establish Redis connection."""
        try:
            self.client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                max_connections=20
            )

            # Test connection
            await self.client.ping()
            self._connected = True
            logger.info(f"Connected to Redis at {self.redis_host}:{self.redis_port}")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._connected = False
            self.client = None
            raise

    async def disconnect(self):
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            self._connected = False
            logger.info("Disconnected from Redis")

    def _generate_cache_key(self, category: str, identifier: str, params: Dict[str, Any] = None) -> str:
        """Generate a consistent cache key."""
        prefix = self.key_prefixes.get(category, f"{category}:")

        # Include parameters in key generation for uniqueness
        if params:
            param_str = json.dumps(params, sort_keys=True)
            param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
            return f"{prefix}{identifier}:{param_hash}"

        return f"{prefix}{identifier}"

    async def set(self, category: str, identifier: str, value: Any, ttl: int = None, params: Dict[str, Any] = None) -> bool:
        """Store value in cache with automatic TTL."""
        if not self._connected or not self.client:
            await self.connect()

        try:
            key = self._generate_cache_key(category, identifier, params)
            cache_ttl = ttl or self.cache_ttl_config.get(category, 1800)

            # Add metadata to cached value
            cache_data = {
                "value": value,
                "cached_at": datetime.now().isoformat(),
                "category": category,
                "identifier": identifier,
                "params": params or {},
                "ttl": cache_ttl
            }

            serialized_data = json.dumps(cache_data, default=str)
            result = await self.client.setex(key, cache_ttl, serialized_data)

            logger.debug(f"Cached {category} data for {identifier} (TTL: {cache_ttl}s)")
            return result

        except Exception as e:
            logger.error(f"Failed to set cache for {category}:{identifier}: {e}")
            return False

    async def get(self, category: str, identifier: str, params: Dict[str, Any] = None) -> Optional[Any]:
        """Retrieve value from cache."""
        if not self._connected or not self.client:
            try:
                await self.connect()
            except Exception:
                return None

        try:
            key = self._generate_cache_key(category, identifier, params)
            cached_data = await self.client.get(key)

            if cached_data:
                cache_obj = json.loads(cached_data)
                logger.debug(f"Cache hit for {category}:{identifier}")
                return cache_obj["value"]

            logger.debug(f"Cache miss for {category}:{identifier}")
            return None

        except Exception as e:
            logger.error(f"Failed to get cache for {category}:{identifier}: {e}")
            return None

    async def delete(self, category: str, identifier: str, params: Dict[str, Any] = None) -> bool:
        """Remove value from cache."""
        if not self._connected or not self.client:
            return False

        try:
            key = self._generate_cache_key(category, identifier, params)
            result = await self.client.delete(key)
            logger.debug(f"Deleted cache for {category}:{identifier}")
            return bool(result)

        except Exception as e:
            logger.error(f"Failed to delete cache for {category}:{identifier}: {e}")
            return False

    async def cache_ai_response(self, prompt: str, response: Dict[str, Any], provider: str = "default",
                              model: str = "default", ttl: int = None) -> bool:
        """Cache AI response with prompt-based key."""
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        identifier = f"{provider}:{model}:{prompt_hash}"

        return await self.set("ai_response", identifier, response, ttl)

    async def get_cached_ai_response(self, prompt: str, provider: str = "default",
                                   model: str = "default") -> Optional[Dict[str, Any]]:
        """Retrieve cached AI response."""
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        identifier = f"{provider}:{model}:{prompt_hash}"

        return await self.get("ai_response", identifier)

    async def cache_api_response(self, endpoint: str, params: Dict[str, Any], response: Any, ttl: int = None) -> bool:
        """Cache API response with endpoint and parameter-based key."""
        return await self.set("api_call", endpoint, response, ttl, params)

    async def get_cached_api_response(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Any]:
        """Retrieve cached API response."""
        return await self.get("api_call", endpoint, params)

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache keys matching a pattern using SCAN (non-blocking)."""
        if not self._connected or not self.client:
            return 0

        try:
            # Use SCAN instead of KEYS to avoid blocking Redis
            keys = []
            cursor = 0
            while True:
                cursor, batch = await self.client.scan(
                    cursor=cursor,
                    match=pattern,
                    count=100
                )
                keys.extend(batch)
                if cursor == 0:
                    break

            if keys:
                result = await self.client.delete(*keys)
                logger.info(f"Invalidated {result} cache keys matching pattern: {pattern}")
                return result
            return 0

        except Exception as e:
            logger.error(f"Failed to invalidate pattern {pattern}: {e}")
            return 0

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics and health information."""
        if not self._connected or not self.client:
            return {"connected": False, "error": "Not connected to Redis"}

        try:
            info = await self.client.info()
            memory_info = await self.client.info("memory")

            # Count keys by category using SCAN (non-blocking)
            category_counts = {}
            for category, prefix in self.key_prefixes.items():
                keys = []
                cursor = 0
                while True:
                    cursor, batch = await self.client.scan(
                        cursor=cursor,
                        match=f"{prefix}*",
                        count=100
                    )
                    keys.extend(batch)
                    if cursor == 0:
                        break
                category_counts[category] = len(keys)

            return {
                "connected": True,
                "total_keys": await self.client.dbsize(),
                "memory_used_mb": round(memory_info["used_memory"] / 1024 / 1024, 2),
                "memory_peak_mb": round(memory_info["used_memory_peak"] / 1024 / 1024, 2),
                "connected_clients": info["connected_clients"],
                "category_counts": category_counts,
                "cache_hit_ratio": info.get("keyspace_hit_ratio", 0),
                "uptime_seconds": info["uptime_in_seconds"],
                "redis_version": info["redis_version"]
            }

        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"connected": False, "error": str(e)}

    async def warm_cache(self, warm_data: Dict[str, Any]) -> Dict[str, int]:
        """Pre-populate cache with commonly accessed data."""
        results = {"success": 0, "failed": 0}

        for category, items in warm_data.items():
            for identifier, value in items.items():
                try:
                    success = await self.set(category, identifier, value)
                    if success:
                        results["success"] += 1
                    else:
                        results["failed"] += 1
                except Exception as e:
                    logger.error(f"Failed to warm cache for {category}:{identifier}: {e}")
                    results["failed"] += 1

        logger.info(f"Cache warming completed: {results['success']} success, {results['failed']} failed")
        return results

    async def cleanup_expired(self) -> Dict[str, int]:
        """Clean up expired cache entries (Redis handles this automatically, but useful for stats)."""
        try:
            info = await self.client.info("stats")
            return {
                "expired_keys": info.get("expired_keys", 0),
                "evicted_keys": info.get("evicted_keys", 0)
            }
        except Exception as e:
            logger.error(f"Failed to get cleanup stats: {e}")
            return {"expired_keys": 0, "evicted_keys": 0}

# Global cache instance
redis_cache = RedisCache()

# Convenience functions for common caching patterns
async def cache_ai_response(prompt: str, response: Dict[str, Any], provider: str = "default") -> bool:
    """Convenience function to cache AI responses."""
    return await redis_cache.cache_ai_response(prompt, response, provider)

async def get_cached_ai_response(prompt: str, provider: str = "default") -> Optional[Dict[str, Any]]:
    """Convenience function to get cached AI responses."""
    return await redis_cache.get_cached_ai_response(prompt, provider)

async def cache_expensive_query(query_id: str, result: Any, ttl: int = 3600) -> bool:
    """Cache results of expensive database queries."""
    return await redis_cache.set("query", query_id, result, ttl)

async def get_cached_query(query_id: str) -> Optional[Any]:
    """Get cached query results."""
    return await redis_cache.get("query", query_id)

async def initialize_redis_cache() -> bool:
    """Initialize the Redis cache connection."""
    try:
        await redis_cache.connect()
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Redis cache: {e}")
        return False