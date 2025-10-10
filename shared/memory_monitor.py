"""
Memory monitoring module for Xynergy platform services.
Phase 3: Reliability & Monitoring

Tracks memory usage and detects potential memory leaks.
"""

import psutil
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class MemorySnapshot:
    """Single memory usage snapshot."""
    timestamp: str
    rss_mb: float  # Resident Set Size (actual physical memory)
    vms_mb: float  # Virtual Memory Size
    percent: float  # Percentage of total system memory
    available_mb: float  # Available system memory


class MemoryMonitor:
    """
    Monitor memory usage for a service and detect leaks.

    Usage:
        monitor = MemoryMonitor("marketing-engine", alert_threshold_mb=500)

        # In startup event:
        asyncio.create_task(monitor.start_monitoring(interval_seconds=60))

        # In shutdown event:
        monitor.stop_monitoring()
    """

    def __init__(
        self,
        service_name: str,
        alert_threshold_mb: int = 500,
        history_size: int = 60  # Keep last 60 snapshots
    ):
        self.service_name = service_name
        self.alert_threshold_mb = alert_threshold_mb
        self.history_size = history_size

        self.process = psutil.Process()
        self.baseline_memory: Optional[float] = None
        self.history: List[MemorySnapshot] = []
        self._monitoring = False
        self._monitoring_task: Optional[asyncio.Task] = None

    def get_memory_usage(self) -> MemorySnapshot:
        """Get current memory usage snapshot."""
        memory_info = self.process.memory_info()
        system_memory = psutil.virtual_memory()

        return MemorySnapshot(
            timestamp=datetime.now().isoformat(),
            rss_mb=memory_info.rss / 1024 / 1024,
            vms_mb=memory_info.vms / 1024 / 1024,
            percent=self.process.memory_percent(),
            available_mb=system_memory.available / 1024 / 1024
        )

    def check_memory_leak(self) -> Dict:
        """
        Check if memory usage is growing abnormally.

        Returns:
            dict with leak detection results
        """
        current = self.get_memory_usage()

        # Set baseline on first check
        if self.baseline_memory is None:
            self.baseline_memory = current.rss_mb
            return {
                "leak_detected": False,
                "current_mb": current.rss_mb,
                "baseline_mb": self.baseline_memory,
                "growth_mb": 0,
                "message": "Baseline established"
            }

        growth = current.rss_mb - self.baseline_memory
        leak_detected = growth > self.alert_threshold_mb

        result = {
            "leak_detected": leak_detected,
            "current_mb": round(current.rss_mb, 2),
            "baseline_mb": round(self.baseline_memory, 2),
            "growth_mb": round(growth, 2),
            "percent_growth": round((growth / self.baseline_memory * 100), 2) if self.baseline_memory > 0 else 0,
            "timestamp": current.timestamp
        }

        if leak_detected:
            result["message"] = f"ALERT: Memory grew {growth:.0f}MB above baseline"
            logger.warning(
                f"[{self.service_name}] Memory leak detected!",
                extra=result
            )

        return result

    def get_memory_trend(self, window_minutes: int = 30) -> Dict:
        """
        Analyze memory trend over recent history.

        Args:
            window_minutes: Time window to analyze

        Returns:
            dict with trend analysis
        """
        if len(self.history) < 2:
            return {
                "trend": "insufficient_data",
                "slope_mb_per_hour": 0,
                "snapshots": len(self.history)
            }

        # Filter to time window
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        recent = [
            s for s in self.history
            if datetime.fromisoformat(s.timestamp) > cutoff_time
        ]

        if len(recent) < 2:
            return {
                "trend": "insufficient_data",
                "slope_mb_per_hour": 0,
                "snapshots": len(recent)
            }

        # Calculate simple linear trend
        first = recent[0]
        last = recent[-1]

        time_diff = (
            datetime.fromisoformat(last.timestamp) -
            datetime.fromisoformat(first.timestamp)
        ).total_seconds() / 3600  # Convert to hours

        if time_diff == 0:
            return {
                "trend": "stable",
                "slope_mb_per_hour": 0,
                "snapshots": len(recent)
            }

        memory_diff = last.rss_mb - first.rss_mb
        slope = memory_diff / time_diff

        # Determine trend category
        if abs(slope) < 10:  # Less than 10MB/hour change
            trend = "stable"
        elif slope > 50:  # Growing more than 50MB/hour
            trend = "growing_fast"
        elif slope > 10:
            trend = "growing"
        elif slope < -10:
            trend = "decreasing"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "slope_mb_per_hour": round(slope, 2),
            "snapshots": len(recent),
            "window_minutes": window_minutes,
            "first_mb": round(first.rss_mb, 2),
            "last_mb": round(last.rss_mb, 2),
            "change_mb": round(memory_diff, 2)
        }

    async def start_monitoring(self, interval_seconds: int = 60):
        """
        Start periodic memory monitoring.

        Args:
            interval_seconds: How often to check memory (default: 60s)
        """
        self._monitoring = True
        self._monitoring_task = asyncio.create_task(
            self._monitoring_loop(interval_seconds)
        )
        logger.info(f"[{self.service_name}] Memory monitoring started (interval: {interval_seconds}s)")

    async def _monitoring_loop(self, interval_seconds: int):
        """Background task for periodic monitoring."""
        while self._monitoring:
            try:
                # Take snapshot
                snapshot = self.get_memory_usage()
                self.history.append(snapshot)

                # Trim history to size limit
                if len(self.history) > self.history_size:
                    self.history = self.history[-self.history_size:]

                # Check for leaks every 10th snapshot (10 minutes if interval=60s)
                if len(self.history) % 10 == 0:
                    leak_check = self.check_memory_leak()
                    trend = self.get_memory_trend(window_minutes=30)

                    logger.info(
                        f"[{self.service_name}] Memory: {snapshot.rss_mb:.0f}MB "
                        f"({snapshot.percent:.1f}%), Trend: {trend['trend']}"
                    )

                    # Alert if fast growth detected
                    if trend["trend"] == "growing_fast":
                        logger.warning(
                            f"[{self.service_name}] Fast memory growth detected: "
                            f"{trend['slope_mb_per_hour']:.1f} MB/hour"
                        )

                await asyncio.sleep(interval_seconds)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[{self.service_name}] Error in memory monitoring: {e}")
                await asyncio.sleep(interval_seconds)

    def stop_monitoring(self):
        """Stop memory monitoring."""
        self._monitoring = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
        logger.info(f"[{self.service_name}] Memory monitoring stopped")

    def get_stats(self) -> Dict:
        """Get comprehensive memory statistics."""
        if not self.history:
            return {"error": "No data collected yet"}

        latest = self.history[-1]
        leak_check = self.check_memory_leak()
        trend_30min = self.get_memory_trend(window_minutes=30)

        # Calculate stats over all history
        all_rss = [s.rss_mb for s in self.history]

        return {
            "service": self.service_name,
            "current": {
                "rss_mb": round(latest.rss_mb, 2),
                "percent": round(latest.percent, 2),
                "timestamp": latest.timestamp
            },
            "baseline_mb": round(self.baseline_memory, 2) if self.baseline_memory else None,
            "leak_detection": leak_check,
            "trend_30min": trend_30min,
            "history": {
                "snapshots": len(self.history),
                "min_mb": round(min(all_rss), 2),
                "max_mb": round(max(all_rss), 2),
                "avg_mb": round(sum(all_rss) / len(all_rss), 2)
            }
        }

    def reset_baseline(self):
        """Reset the memory baseline (e.g., after legitimate growth)."""
        current = self.get_memory_usage()
        self.baseline_memory = current.rss_mb
        logger.info(f"[{self.service_name}] Memory baseline reset to {current.rss_mb:.0f}MB")


# Global registry of monitors for easy access
_monitors: Dict[str, MemoryMonitor] = {}


def get_memory_monitor(service_name: str, **kwargs) -> MemoryMonitor:
    """
    Get or create a memory monitor for a service.

    This allows easy access to the monitor from anywhere in the service:

    Example:
        from shared.memory_monitor import get_memory_monitor

        monitor = get_memory_monitor("my-service")
        stats = monitor.get_stats()
    """
    if service_name not in _monitors:
        _monitors[service_name] = MemoryMonitor(service_name, **kwargs)
    return _monitors[service_name]


def shutdown_all_monitors():
    """Stop all active memory monitors."""
    for monitor in _monitors.values():
        monitor.stop_monitoring()
    _monitors.clear()
