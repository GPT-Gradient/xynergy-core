"""
Rate Limiting for Xynergy Platform
Prevents abuse and controls costs on AI/expensive endpoints.
"""

import os
import time
from typing import Dict, Optional
from collections import defaultdict
from datetime import datetime, timedelta
import threading
from fastapi import HTTPException, Request, status
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    In-memory rate limiter with sliding window algorithm.
    For production, use Redis-based rate limiting for distributed systems.
    """

    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_limit: int = 100
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_limit = burst_limit

        # Storage with max size to prevent unbounded growth
        # Using LRU cache for most recent identifiers (max 10,000)
        from cachetools import LRUCache
        self.minute_requests = LRUCache(maxsize=10000)
        self.hour_requests = LRUCache(maxsize=10000)
        self.lock = threading.Lock()

        # Cleanup thread
        self._start_cleanup_thread()

    def _cleanup_old_requests(self):
        """Remove expired request records."""
        now = time.time()
        minute_ago = now - 60
        hour_ago = now - 3600

        with self.lock:
            # Clean minute records (LRUCache is dict-like but has max size)
            try:
                for key in list(self.minute_requests.keys()):
                    if key in self.minute_requests:
                        requests = self.minute_requests[key]
                        filtered = [
                            (ts, count) for ts, count in requests
                            if ts > minute_ago
                        ]
                        if filtered:
                            self.minute_requests[key] = filtered
                        else:
                            del self.minute_requests[key]
            except RuntimeError:
                pass  # Dict size changed during iteration

            # Clean hour records
            try:
                for key in list(self.hour_requests.keys()):
                    if key in self.hour_requests:
                        requests = self.hour_requests[key]
                        filtered = [
                            (ts, count) for ts, count in requests
                            if ts > hour_ago
                        ]
                        if filtered:
                            self.hour_requests[key] = filtered
                        else:
                            del self.hour_requests[key]
            except RuntimeError:
                pass  # Dict size changed during iteration

    def _start_cleanup_thread(self):
        """Start background cleanup thread."""
        def cleanup_loop():
            while True:
                time.sleep(60)  # Cleanup every minute
                try:
                    self._cleanup_old_requests()
                except Exception as e:
                    logger.error(f"Rate limiter cleanup error: {e}")

        thread = threading.Thread(target=cleanup_loop, daemon=True)
        thread.start()

    def check_rate_limit(self, identifier: str, cost: int = 1) -> Dict[str, any]:
        """
        Check if request is within rate limits.

        Args:
            identifier: Unique identifier (API key, IP address, etc.)
            cost: Cost weight of this request (default 1, AI requests might be 10)

        Returns:
            Dict with limit info

        Raises:
            HTTPException: If rate limit exceeded
        """
        now = time.time()

        with self.lock:
            # Check minute limit
            minute_count = sum(
                count for ts, count in self.minute_requests.get(identifier, [])
                if ts > (now - 60)
            )

            if minute_count + cost > self.requests_per_minute:
                reset_time = int(now - (now % 60) + 60)
                logger.warning(
                    f"Rate limit exceeded (minute): {identifier[:8]}... "
                    f"({minute_count}/{self.requests_per_minute})"
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded: {self.requests_per_minute} requests per minute",
                    headers={
                        "X-RateLimit-Limit": str(self.requests_per_minute),
                        "X-RateLimit-Remaining": str(max(0, self.requests_per_minute - minute_count)),
                        "X-RateLimit-Reset": str(reset_time),
                        "Retry-After": str(reset_time - int(now))
                    }
                )

            # Check hour limit
            hour_count = sum(
                count for ts, count in self.hour_requests.get(identifier, [])
                if ts > (now - 3600)
            )

            if hour_count + cost > self.requests_per_hour:
                reset_time = int(now - (now % 3600) + 3600)
                logger.warning(
                    f"Rate limit exceeded (hour): {identifier[:8]}... "
                    f"({hour_count}/{self.requests_per_hour})"
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded: {self.requests_per_hour} requests per hour",
                    headers={
                        "X-RateLimit-Limit": str(self.requests_per_hour),
                        "X-RateLimit-Remaining": str(max(0, self.requests_per_hour - hour_count)),
                        "X-RateLimit-Reset": str(reset_time),
                        "Retry-After": str(reset_time - int(now))
                    }
                )

            # Record this request
            if identifier not in self.minute_requests:
                self.minute_requests[identifier] = []
            if identifier not in self.hour_requests:
                self.hour_requests[identifier] = []
            self.minute_requests[identifier].append((now, cost))
            self.hour_requests[identifier].append((now, cost))

            return {
                "minute_remaining": self.requests_per_minute - (minute_count + cost),
                "hour_remaining": self.requests_per_hour - (hour_count + cost),
                "minute_limit": self.requests_per_minute,
                "hour_limit": self.requests_per_hour
            }

    async def check_request_rate(self, request: Request, cost: int = 1) -> None:
        """
        FastAPI dependency for rate limiting.

        Usage:
            @app.post("/api/expensive", dependencies=[Depends(rate_limiter.check_request_rate)])
        """
        # Get identifier from API key or IP address
        identifier = None

        # Try to get from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            identifier = auth_header[7:]  # API key
        else:
            # Fallback to IP address
            identifier = request.client.host if request.client else "unknown"

        self.check_rate_limit(identifier, cost)


# Global rate limiters for different endpoint types
standard_rate_limiter = RateLimiter(
    requests_per_minute=60,
    requests_per_hour=1000,
    burst_limit=100
)

ai_rate_limiter = RateLimiter(
    requests_per_minute=10,   # AI is expensive
    requests_per_hour=100,
    burst_limit=20
)

expensive_rate_limiter = RateLimiter(
    requests_per_minute=5,
    requests_per_hour=50,
    burst_limit=10
)


# Convenience dependency functions
async def rate_limit_standard(request: Request):
    """Standard rate limit for most endpoints."""
    await standard_rate_limiter.check_request_rate(request, cost=1)


async def rate_limit_ai(request: Request):
    """Strict rate limit for AI generation endpoints."""
    await ai_rate_limiter.check_request_rate(request, cost=10)


async def rate_limit_expensive(request: Request):
    """Very strict rate limit for expensive operations."""
    await expensive_rate_limiter.check_request_rate(request, cost=20)


__all__ = [
    "RateLimiter",
    "rate_limit_standard",
    "rate_limit_ai",
    "rate_limit_expensive",
]
