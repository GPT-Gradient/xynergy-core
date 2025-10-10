"""
ASO Service - Integration with Xynergy ASO Engine
Handles all communication with the ASO Engine for trending keywords, rankings, and content performance
"""

import time
from typing import List, Dict, Any, Optional
import httpx
import structlog

logger = structlog.get_logger()


class ASOService:
    """Service for interacting with Xynergy ASO Engine"""

    def __init__(self, aso_engine_url: str):
        self.aso_engine_url = aso_engine_url.rstrip('/')
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(5.0, connect=2.0),
            http2=True
        )
        self.circuit_breaker_failures = 0
        self.circuit_breaker_last_failure = 0
        self.circuit_breaker_threshold = 3
        self.circuit_breaker_timeout = 60  # seconds

    def is_circuit_open(self) -> bool:
        """Check if circuit breaker is open"""
        if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
            if time.time() - self.circuit_breaker_last_failure < self.circuit_breaker_timeout:
                return True
            # Reset circuit breaker after timeout
            self.circuit_breaker_failures = 0
        return False

    def record_failure(self):
        """Record a failure for circuit breaker"""
        self.circuit_breaker_failures += 1
        self.circuit_breaker_last_failure = time.time()
        logger.warning(
            "aso_service_failure_recorded",
            failures=self.circuit_breaker_failures,
            threshold=self.circuit_breaker_threshold
        )

    def record_success(self):
        """Record a success (reset circuit breaker)"""
        if self.circuit_breaker_failures > 0:
            logger.info("aso_service_recovered", previous_failures=self.circuit_breaker_failures)
        self.circuit_breaker_failures = 0

    async def health_check(self) -> Dict[str, Any]:
        """Check if ASO Engine is healthy"""
        try:
            start = time.time()
            response = await self.client.get(f"{self.aso_engine_url}/health", timeout=3.0)
            response_time = int((time.time() - start) * 1000)

            if response.status_code == 200:
                self.record_success()
                return {
                    "status": "healthy",
                    "response_time_ms": response_time
                }
            else:
                self.record_failure()
                return {
                    "status": "unhealthy",
                    "http_status": response.status_code
                }
        except Exception as e:
            self.record_failure()
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    async def get_trending_keywords(
        self,
        tenant_id: str = "clearforge",
        limit: int = 20,
        min_volume: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get trending keywords from ASO Engine

        Returns enriched keyword data with trend scores and opportunity metrics
        """
        if self.is_circuit_open():
            logger.warning("aso_circuit_breaker_open", action="returning_empty_data")
            return []

        try:
            response = await self.client.get(
                f"{self.aso_engine_url}/api/keywords/trending",
                params={
                    "tenant_id": tenant_id,
                    "limit": limit,
                    "min_volume": min_volume
                }
            )
            response.raise_for_status()

            data = response.json()
            keywords = data.get("keywords", [])

            # Transform data for frontend consumption
            enriched_keywords = []
            for kw in keywords:
                enriched_keywords.append({
                    "keyword": kw.get("keyword", ""),
                    "search_volume": kw.get("search_volume", 0),
                    "trend_score": kw.get("trend_score", 0) or self._calculate_trend_score(kw),
                    "growth_rate": kw.get("growth_rate", 0) or self._calculate_growth_rate(kw),
                    "difficulty_score": kw.get("difficulty_score", 50),
                    "opportunity_score": kw.get("opportunity_score", 0) or self._calculate_opportunity_score(kw)
                })

            self.record_success()
            return enriched_keywords

        except httpx.TimeoutException:
            logger.error("aso_trending_keywords_timeout", tenant_id=tenant_id)
            self.record_failure()
            return []
        except httpx.HTTPStatusError as e:
            logger.error("aso_trending_keywords_http_error", status_code=e.response.status_code)
            self.record_failure()
            return []
        except Exception as e:
            logger.error("aso_trending_keywords_error", error=str(e))
            self.record_failure()
            return []

    async def get_keyword_rankings(
        self,
        tenant_id: str = "clearforge",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get current keyword rankings for tenant's content

        Returns rankings with position changes and URLs
        """
        if self.is_circuit_open():
            logger.warning("aso_circuit_breaker_open", action="returning_empty_rankings")
            return []

        try:
            # Get content list with rankings
            response = await self.client.get(
                f"{self.aso_engine_url}/api/content",
                params={
                    "tenant_id": tenant_id,
                    "status": "published",
                    "limit": limit
                }
            )
            response.raise_for_status()

            data = response.json()
            content_list = data.get("content", [])

            # Transform to rankings format
            rankings = []
            for content in content_list:
                if content.get("ranking_position"):
                    rankings.append({
                        "keyword": content.get("keyword_primary", ""),
                        "content_id": content.get("content_id", ""),
                        "content_title": content.get("title", ""),
                        "current_position": content.get("ranking_position", 0),
                        "previous_position": content.get("previous_position", content.get("ranking_position", 0)),
                        "change": self._calculate_position_change(content),
                        "url": content.get("url", "")
                    })

            self.record_success()
            return rankings

        except Exception as e:
            logger.error("aso_keyword_rankings_error", error=str(e))
            self.record_failure()
            return []

    async def get_content_performance(
        self,
        tenant_id: str = "clearforge",
        period_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get aggregated content performance metrics

        Returns performance data with views, conversions, and scores
        """
        if self.is_circuit_open():
            logger.warning("aso_circuit_breaker_open", action="returning_empty_performance")
            return []

        try:
            response = await self.client.get(
                f"{self.aso_engine_url}/api/content",
                params={
                    "tenant_id": tenant_id,
                    "limit": 100
                }
            )
            response.raise_for_status()

            data = response.json()
            content_list = data.get("content", [])

            # Transform to performance format
            performance = []
            for content in content_list:
                performance.append({
                    "content_id": content.get("content_id", ""),
                    "title": content.get("title", ""),
                    "content_type": content.get("content_type", "spoke"),
                    "total_views": content.get("monthly_traffic", 0),
                    "total_conversions": content.get("monthly_conversions", 0),
                    "conversion_rate": content.get("conversion_rate", 0),
                    "avg_position": content.get("ranking_position", 0),
                    "performance_score": content.get("performance_score", 0),
                    "trend": self._determine_trend(content)
                })

            self.record_success()
            return performance

        except Exception as e:
            logger.error("aso_content_performance_error", error=str(e))
            self.record_failure()
            return []

    # Helper methods for data enrichment

    def _calculate_trend_score(self, keyword_data: Dict) -> float:
        """Calculate trend score based on available data"""
        # If no trend data, return moderate score
        search_volume = keyword_data.get("search_volume", 0)
        if search_volume > 10000:
            return 90.0
        elif search_volume > 5000:
            return 75.0
        elif search_volume > 1000:
            return 60.0
        else:
            return 45.0

    def _calculate_growth_rate(self, keyword_data: Dict) -> float:
        """Calculate growth rate percentage"""
        # Placeholder - would use historical data in production
        trend = keyword_data.get("trend", "stable")
        if trend == "rising":
            return 125.0
        elif trend == "falling":
            return -25.0
        else:
            return 0.0

    def _calculate_opportunity_score(self, keyword_data: Dict) -> float:
        """Calculate opportunity score (0-100)"""
        search_volume = keyword_data.get("search_volume", 0)
        difficulty = keyword_data.get("difficulty_score", 50)

        # High volume, low difficulty = high opportunity
        volume_score = min(search_volume / 100, 50)  # Max 50 points
        difficulty_score = (100 - difficulty) / 2  # Max 50 points

        return round(volume_score + difficulty_score, 1)

    def _calculate_position_change(self, content_data: Dict) -> int:
        """Calculate position change (positive = improved)"""
        current = content_data.get("ranking_position", 0)
        previous = content_data.get("previous_position", current)

        # Position improvement means number goes down
        # So change = previous - current (e.g., 5 -> 3 = +2 improvement)
        return previous - current

    def _determine_trend(self, content_data: Dict) -> str:
        """Determine content trend (rising, falling, stable)"""
        change = self._calculate_position_change(content_data)
        if change > 2:
            return "rising"
        elif change < -2:
            return "falling"
        else:
            return "stable"
