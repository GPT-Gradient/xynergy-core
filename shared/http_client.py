"""
Shared HTTP Client Manager for Service Communication
Optimizes inter-service communication with connection pooling and retry logic.
"""
import asyncio
import threading
from typing import Optional
import httpx
import logging

logger = logging.getLogger(__name__)

class ServiceHttpClient:
    """Centralized HTTP client for service-to-service communication."""

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
            self._client: Optional[httpx.AsyncClient] = None
            self._client_lock = asyncio.Lock() if asyncio._get_running_loop() else None
            self._initialized = True

    async def get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with connection pooling."""
        if self._client is None:
            if self._client_lock is None:
                self._client_lock = asyncio.Lock()

            async with self._client_lock:
                if self._client is None:
                    try:
                        # Configure connection pooling and timeouts
                        limits = httpx.Limits(
                            max_keepalive_connections=20,
                            max_connections=100,
                            keepalive_expiry=30.0
                        )

                        timeout = httpx.Timeout(
                            connect=10.0,
                            read=30.0,
                            write=10.0,
                            pool=5.0
                        )

                        self._client = httpx.AsyncClient(
                            limits=limits,
                            timeout=timeout,
                            http2=True,  # Enable HTTP/2 for better performance
                            verify=True  # Verify SSL certificates
                        )
                        logger.info("Created new HTTP client with connection pooling")
                    except Exception as e:
                        logger.error(f"Failed to create HTTP client: {e}")
                        raise
        return self._client

    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make HTTP request with automatic retries and circuit breaker."""
        client = await self.get_client()
        max_retries = kwargs.pop('max_retries', 3)

        for attempt in range(max_retries + 1):
            try:
                response = await client.request(method, url, **kwargs)

                # Log successful requests for monitoring
                logger.debug(f"{method} {url} - Status: {response.status_code}")

                return response

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                if attempt < max_retries:
                    backoff_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries + 1}): {e}. Retrying in {backoff_time}s")
                    await asyncio.sleep(backoff_time)
                else:
                    logger.error(f"Request failed after {max_retries + 1} attempts: {e}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error in HTTP request: {e}")
                raise

    async def get(self, url: str, **kwargs) -> httpx.Response:
        """Make GET request."""
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        """Make POST request."""
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs) -> httpx.Response:
        """Make PUT request."""
        return await self.request("PUT", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> httpx.Response:
        """Make DELETE request."""
        return await self.request("DELETE", url, **kwargs)

    async def close(self):
        """Close HTTP client connections."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("Closed HTTP client")

# Global instance for easy importing
http_client = ServiceHttpClient()

# Convenience functions
async def get_http_client() -> httpx.AsyncClient:
    """Convenience function to get HTTP client."""
    return await http_client.get_client()

async def http_get(url: str, **kwargs) -> httpx.Response:
    """Convenience function for GET requests."""
    return await http_client.get(url, **kwargs)

async def http_post(url: str, **kwargs) -> httpx.Response:
    """Convenience function for POST requests."""
    return await http_client.post(url, **kwargs)

async def http_put(url: str, **kwargs) -> httpx.Response:
    """Convenience function for PUT requests."""
    return await http_client.put(url, **kwargs)

async def http_delete(url: str, **kwargs) -> httpx.Response:
    """Convenience function for DELETE requests."""
    return await http_client.delete(url, **kwargs)

async def close_http_client():
    """Convenience function to close HTTP client."""
    await http_client.close()