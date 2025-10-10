"""
Centralized Authentication Module for Xynergy Platform
Provides secure API key validation with zero-trust principles.
"""

import os
from typing import Optional, Set
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

# Load API keys from environment with validation
def load_api_keys() -> Set[str]:
    """Load and validate API keys from environment variable."""
    keys_string = os.getenv("XYNERGY_API_KEYS", "")

    if not keys_string:
        logger.warning("XYNERGY_API_KEYS environment variable not set - authentication disabled!")
        return set()

    # Split, filter empty, and create set
    keys = set(filter(None, [key.strip() for key in keys_string.split(",")]))

    if not keys:
        logger.warning("No valid API keys found in XYNERGY_API_KEYS")
        return set()

    logger.info(f"Loaded {len(keys)} valid API keys")
    return keys


# Global API key store
VALID_API_KEYS: Set[str] = load_api_keys()


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
    if not VALID_API_KEYS:
        logger.error("API authentication attempted but no keys configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API authentication not configured - contact system administrator",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate the provided key
    if credentials.credentials not in VALID_API_KEYS:
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

    if not VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API authentication not configured",
        )

    if x_api_key not in VALID_API_KEYS:
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
    "VALID_API_KEYS",
    "RateLimitConfig",
]
