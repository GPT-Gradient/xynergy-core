"""
Centralized Authentication Module for Xynergy Platform
Provides secure API key validation with zero-trust principles.
"""

import os
from typing import Optional, Set
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import time
import threading

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

# Global API key store with thread-safe access
class APIKeyManager:
    """Thread-safe API key manager with automatic rotation support."""

    def __init__(self, reload_interval: int = 300):
        """
        Initialize API key manager.

        Args:
            reload_interval: Seconds between automatic reloads (default 5 minutes)
        """
        self._keys: Set[str] = set()
        self._lock = threading.RLock()
        self._last_reload = 0
        self._reload_interval = reload_interval
        self._load_keys()

    def _load_keys(self) -> None:
        """Load API keys from environment variable."""
        keys_string = os.getenv("XYNERGY_API_KEYS", "")

        if not keys_string:
            logger.warning("XYNERGY_API_KEYS environment variable not set - authentication disabled!")
            with self._lock:
                self._keys = set()
            return

        # Split, filter empty, and create set
        keys = set(filter(None, [key.strip() for key in keys_string.split(",")]))

        if not keys:
            logger.warning("No valid API keys found in XYNERGY_API_KEYS")
            with self._lock:
                self._keys = set()
            return

        with self._lock:
            old_count = len(self._keys)
            self._keys = keys
            self._last_reload = time.time()

        logger.info(f"Loaded {len(keys)} valid API keys (was {old_count})")

    def reload(self) -> int:
        """Force reload API keys from environment. Returns number of keys loaded."""
        self._load_keys()
        return len(self._keys)

    def get_keys(self) -> Set[str]:
        """Get current API keys, reloading if past interval."""
        # Auto-reload if past interval
        if time.time() - self._last_reload > self._reload_interval:
            self._load_keys()

        with self._lock:
            return self._keys.copy()

    def validate_key(self, key: str) -> bool:
        """Check if a key is valid."""
        return key in self.get_keys()


# Global API key manager (auto-reloads every 5 minutes)
_api_key_manager = APIKeyManager(reload_interval=300)

# Backward compatibility
VALID_API_KEYS: Set[str] = _api_key_manager.get_keys()

def reload_api_keys() -> int:
    """Reload API keys from environment. Returns number of keys loaded."""
    return _api_key_manager.reload()


async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Verify API key from Bearer token.

    Args:
        credentials: HTTP Bearer credentials from request header

    Returns:
        The validated API key

    Raises:
        HTTPException: If API key is invalid or not configured
    """
    # Check if API keys are configured
    keys = _api_key_manager.get_keys()
    if not keys:
        logger.error("API authentication attempted but no keys configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API authentication not configured - contact system administrator",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate the provided key
    if not _api_key_manager.validate_key(credentials.credentials):
        logger.warning(f"Invalid API key attempt: {credentials.credentials[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug(f"API key validated successfully: {credentials.credentials[:8]}...")
    return credentials.credentials


async def verify_api_key_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    Optional API key verification for public endpoints with premium features.

    Args:
        credentials: Optional HTTP Bearer credentials

    Returns:
        The API key if provided and valid, None otherwise
    """
    if not credentials:
        return None

    try:
        return await verify_api_key(credentials)
    except HTTPException:
        return None


async def verify_api_key_header(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> str:
    """
    Verify API key from custom X-API-Key header (alternative to Bearer token).

    Args:
        x_api_key: API key from X-API-Key header

    Returns:
        The validated API key

    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header required",
        )

    keys = _api_key_manager.get_keys()
    if not keys:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API authentication not configured",
        )

    if not _api_key_manager.validate_key(x_api_key):
        logger.warning(f"Invalid X-API-Key attempt: {x_api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return x_api_key


def require_auth(func):
    """
    Decorator to require authentication on FastAPI endpoints.

    Usage:
        @app.post("/api/sensitive")
        @require_auth
        async def sensitive_endpoint():
            return {"status": "authenticated"}
    """
    from functools import wraps

    @wraps(func)
    async def wrapper(*args, api_key: str = Depends(verify_api_key), **kwargs):
        return await func(*args, **kwargs)

    return wrapper


# Rate limiting helpers
class RateLimitConfig:
    """Configuration for rate limiting."""

    def __init__(
        self,
        max_requests_per_minute: int = 60,
        max_requests_per_hour: int = 1000,
        burst_limit: int = 100
    ):
        self.max_requests_per_minute = max_requests_per_minute
        self.max_requests_per_hour = max_requests_per_hour
        self.burst_limit = burst_limit


# Export commonly used functions
__all__ = [
    "verify_api_key",
    "verify_api_key_optional",
    "verify_api_key_header",
    "require_auth",
    "reload_api_keys",
    "VALID_API_KEYS",
    "RateLimitConfig",
]
