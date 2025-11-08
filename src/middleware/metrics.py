"""
Metrics middleware for tracking response time and success rate.
"""
from fastapi import Request, status
from typing import Callable
import time
from collections import defaultdict
from datetime import datetime, timedelta
import threading

from src.utils.logger import get_logger

logger = get_logger("middleware.metrics")


class MetricsCollector:
    """
    Thread-safe metrics collector for API endpoints.
    Tracks response times and success rates per endpoint.
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._response_times = defaultdict(list)  # {endpoint: [times]}
        self._request_counts = defaultdict(int)  # {endpoint: count}
        self._success_counts = defaultdict(int)  # {endpoint: success_count}
        self._error_counts = defaultdict(int)  # {endpoint: error_count}
        self._window_size = 3600  # 1 hour window
        self._max_samples = 1000  # Max samples per endpoint
    
    def record_request(
        self,
        endpoint: str,
        response_time: float,
        status_code: int
    ):
        """
        Record a request with its response time and status code.
        
        Args:
            endpoint: Endpoint path
            response_time: Response time in seconds
            status_code: HTTP status code
        """
        with self._lock:
            # Record response time
            times = self._response_times[endpoint]
            times.append(response_time)
            
            # Keep only recent samples
            if len(times) > self._max_samples:
                times.pop(0)
            
            # Record counts
            self._request_counts[endpoint] += 1
            
            # Record success/error
            if 200 <= status_code < 400:
                self._success_counts[endpoint] += 1
            else:
                self._error_counts[endpoint] += 1
    
    def get_metrics(self, endpoint: str | None = None) -> dict:
        """
        Get metrics for a specific endpoint or all endpoints.
        
        Args:
            endpoint: Optional endpoint path. If None, returns metrics for all endpoints.
        
        Returns:
            Dictionary with metrics
        """
        with self._lock:
            if endpoint:
                return self._get_endpoint_metrics(endpoint)
            else:
                return self._get_all_metrics()
    
    def _get_endpoint_metrics(self, endpoint: str) -> dict:
        """Get metrics for a specific endpoint."""
        times = self._response_times.get(endpoint, [])
        request_count = self._request_counts.get(endpoint, 0)
        success_count = self._success_counts.get(endpoint, 0)
        error_count = self._error_counts.get(endpoint, 0)
        
        if not times:
            return {
                "endpoint": endpoint,
                "request_count": request_count,
                "success_count": success_count,
                "error_count": error_count,
                "success_rate": 0.0,
                "avg_response_time": 0.0,
                "min_response_time": 0.0,
                "max_response_time": 0.0,
                "p50_response_time": 0.0,
                "p95_response_time": 0.0,
                "p99_response_time": 0.0
            }
        
        sorted_times = sorted(times)
        n = len(sorted_times)
        
        return {
            "endpoint": endpoint,
            "request_count": request_count,
            "success_count": success_count,
            "error_count": error_count,
            "success_rate": success_count / request_count if request_count > 0 else 0.0,
            "avg_response_time": sum(times) / n,
            "min_response_time": min(times),
            "max_response_time": max(times),
            "p50_response_time": sorted_times[int(n * 0.5)],
            "p95_response_time": sorted_times[int(n * 0.95)] if n > 0 else 0.0,
            "p99_response_time": sorted_times[int(n * 0.99)] if n > 0 else 0.0
        }
    
    def _get_all_metrics(self) -> dict:
        """Get metrics for all endpoints."""
        all_endpoints = set(self._request_counts.keys())
        
        return {
            "endpoints": {
                endpoint: self._get_endpoint_metrics(endpoint)
                for endpoint in all_endpoints
            },
            "summary": {
                "total_requests": sum(self._request_counts.values()),
                "total_success": sum(self._success_counts.values()),
                "total_errors": sum(self._error_counts.values()),
                "overall_success_rate": (
                    sum(self._success_counts.values()) / sum(self._request_counts.values())
                    if sum(self._request_counts.values()) > 0 else 0.0
                )
            }
        }
    
    def reset(self):
        """Reset all metrics."""
        with self._lock:
            self._response_times.clear()
            self._request_counts.clear()
            self._success_counts.clear()
            self._error_counts.clear()


# Global metrics collector instance
_metrics_collector = MetricsCollector()


async def metrics_middleware(request: Request, call_next: Callable):
    """
    Metrics middleware that tracks response time and success rate.
    
    This middleware should be added after rate limiting but before request logging.
    """
    # Skip metrics for health check and docs
    if request.url.path in ["/", "/docs", "/openapi.json", "/redoc", "/metrics"]:
        return await call_next(request)
    
    start_time = time.time()
    endpoint = request.url.path
    
    try:
        response = await call_next(request)
        response_time = time.time() - start_time
        status_code = response.status_code
        
        # Record metrics
        _metrics_collector.record_request(endpoint, response_time, status_code)
        
        # Add response time header
        response.headers["X-Response-Time"] = f"{response_time:.3f}"
        
        return response
    except Exception as e:
        response_time = time.time() - start_time
        status_code = 500
        
        # Record metrics for error
        _metrics_collector.record_request(endpoint, response_time, status_code)
        
        raise


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return _metrics_collector

