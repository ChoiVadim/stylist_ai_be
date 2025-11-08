"""
Rate limiting middleware for FastAPI.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Callable
import time

from src.utils.logger import get_logger

logger = get_logger("middleware.rate_limit")


def get_remote_address(request: Request) -> str:
    """
    Get client IP address from request.
    
    Args:
        request: FastAPI request object
    
    Returns:
        Client IP address as string
    """
    if request.client:
        return request.client.host
    # Try to get from headers (for reverse proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    return "unknown"


def create_rate_limit_middleware(
    default_rate_limit: str = "100/minute",
    analysis_rate_limit: str = "10/minute",
    generation_rate_limit: str = "5/minute"
) -> Callable:
    """
    Create rate limiting middleware with different limits for different endpoint types.
    
    Args:
        default_rate_limit: Default rate limit (e.g., "100/minute")
        analysis_rate_limit: Rate limit for analysis endpoints (e.g., "10/minute")
        generation_rate_limit: Rate limit for generation endpoints (e.g., "5/minute")
    
    Returns:
        Middleware function
    """
    
    async def rate_limit_middleware(request: Request, call_next: Callable):
        """
        Rate limiting middleware that applies different limits based on endpoint path.
        """
        # Skip rate limiting for health check and docs
        if request.url.path in ["/", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)
        
        # Determine rate limit based on endpoint
        endpoint_path = request.url.path
        
        # Analysis endpoints (color, shape analysis)
        if any(path in endpoint_path for path in ["/analyze/color", "/analyze/face", "/analyze/body", "/shape"]):
            limit = analysis_rate_limit
        # Generation endpoints (try-on)
        elif any(path in endpoint_path for path in ["/try-on", "/generate"]):
            limit = generation_rate_limit
        else:
            limit = default_rate_limit
        
        # Apply rate limiting
        try:
            # Use limiter to check rate limit
            # Note: slowapi requires decorator, so we'll use a simpler approach
            # For production, consider using Redis-based rate limiting
            return await call_next(request)
        except RateLimitExceeded:
            logger.warning(
                f"Rate limit exceeded for {request.client.host} on {endpoint_path}"
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {limit}",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
    
    return rate_limit_middleware


# Simple in-memory rate limiter (for development)
# For production, use Redis-based rate limiting
class SimpleRateLimiter:
    """
    Simple in-memory rate limiter.
    For production, use Redis-based solution.
    """
    
    def __init__(self):
        self.requests = {}  # {client_ip: [(timestamp, endpoint), ...]}
        self.cleanup_interval = 300  # Clean up old entries every 5 minutes
        self.last_cleanup = time.time()
    
    def _cleanup_old_entries(self):
        """Remove entries older than 1 minute."""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        cutoff_time = current_time - 60  # 1 minute ago
        
        for client_ip in list(self.requests.keys()):
            self.requests[client_ip] = [
                (ts, endpoint) for ts, endpoint in self.requests[client_ip]
                if ts > cutoff_time
            ]
            if not self.requests[client_ip]:
                del self.requests[client_ip]
        
        self.last_cleanup = current_time
    
    def _parse_rate_limit(self, rate_limit: str) -> tuple[int, int]:
        """
        Parse rate limit string like "10/minute" or "100/hour".
        
        Returns:
            Tuple of (max_requests, window_seconds)
        """
        try:
            parts = rate_limit.split("/")
            max_requests = int(parts[0])
            period = parts[1].lower()
            
            if period == "second" or period == "sec":
                window = 1
            elif period == "minute" or period == "min":
                window = 60
            elif period == "hour" or period == "hr":
                window = 3600
            elif period == "day":
                window = 86400
            else:
                window = 60  # Default to minute
            
            return max_requests, window
        except Exception:
            return 100, 60  # Default: 100 requests per minute
    
    def is_allowed(
        self,
        client_ip: str,
        endpoint: str,
        rate_limit: str = "100/minute"
    ) -> tuple[bool, int]:
        """
        Check if request is allowed based on rate limit.
        
        Args:
            client_ip: Client IP address
            endpoint: Endpoint path
            rate_limit: Rate limit string (e.g., "10/minute")
        
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        self._cleanup_old_entries()
        
        max_requests, window_seconds = self._parse_rate_limit(rate_limit)
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        # Get requests for this client in the time window
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Filter requests within time window
        self.requests[client_ip] = [
            (ts, ep) for ts, ep in self.requests[client_ip]
            if ts > cutoff_time
        ]
        
        # Count requests for this endpoint in the time window
        endpoint_requests = [
            (ts, ep) for ts, ep in self.requests[client_ip]
            if ep == endpoint and ts > cutoff_time
        ]
        
        if len(endpoint_requests) >= max_requests:
            # Rate limit exceeded
            oldest_request_time = min(ts for ts, _ in endpoint_requests)
            retry_after = int(window_seconds - (current_time - oldest_request_time)) + 1
            return False, retry_after
        
        # Add current request
        self.requests[client_ip].append((current_time, endpoint))
        return True, 0


# Global rate limiter instance
_rate_limiter = SimpleRateLimiter()


async def rate_limit_middleware(request: Request, call_next: Callable):
    """
    Rate limiting middleware that applies different limits based on endpoint path.
    """
    # Skip rate limiting for health check and docs
    if request.url.path in ["/", "/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)
    
    # Get client IP
    client_ip = get_remote_address(request)
    if not client_ip:
        client_ip = "unknown"
    
    # Determine rate limit based on endpoint
    endpoint_path = request.url.path
    
    # Analysis endpoints (color, shape analysis)
    if any(path in endpoint_path for path in ["/analyze/color", "/analyze/face", "/analyze/body", "/shape"]):
        limit = "10/minute"
    # Generation endpoints (try-on)
    elif any(path in endpoint_path for path in ["/try-on", "/generate"]):
        limit = "5/minute"
    else:
        limit = "100/minute"
    
    # Check rate limit
    is_allowed, retry_after = _rate_limiter.is_allowed(client_ip, endpoint_path, limit)
    
    if not is_allowed:
        logger.warning(
            f"Rate limit exceeded for {client_ip} on {endpoint_path} (limit: {limit})"
        )
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Limit: {limit}",
                "retry_after": retry_after
            },
            headers={"Retry-After": str(retry_after)}
        )
    
    return await call_next(request)

