"""
Unit tests for rate limiting middleware.
"""
import pytest
import time
from unittest.mock import Mock, AsyncMock

from src.middleware.rate_limit import SimpleRateLimiter, get_remote_address


class TestSimpleRateLimiter:
    """Tests for SimpleRateLimiter."""
    
    def test_parse_rate_limit_minute(self):
        """Test parsing rate limit string for minutes."""
        limiter = SimpleRateLimiter()
        max_requests, window = limiter._parse_rate_limit("10/minute")
        assert max_requests == 10
        assert window == 60
    
    def test_parse_rate_limit_hour(self):
        """Test parsing rate limit string for hours."""
        limiter = SimpleRateLimiter()
        max_requests, window = limiter._parse_rate_limit("100/hour")
        assert max_requests == 100
        assert window == 3600
    
    def test_parse_rate_limit_second(self):
        """Test parsing rate limit string for seconds."""
        limiter = SimpleRateLimiter()
        max_requests, window = limiter._parse_rate_limit("5/second")
        assert max_requests == 5
        assert window == 1
    
    def test_rate_limit_allows_requests(self):
        """Test that rate limiter allows requests within limit."""
        limiter = SimpleRateLimiter()
        client_ip = "127.0.0.1"
        endpoint = "/api/analyze/color"
        
        # First 10 requests should be allowed
        for i in range(10):
            is_allowed, retry_after = limiter.is_allowed(
                client_ip, endpoint, "10/minute"
            )
            assert is_allowed is True
            assert retry_after == 0
    
    def test_rate_limit_blocks_excess_requests(self):
        """Test that rate limiter blocks requests exceeding limit."""
        limiter = SimpleRateLimiter()
        client_ip = "127.0.0.1"
        endpoint = "/api/analyze/color"
        
        # Make 10 requests (at limit)
        for i in range(10):
            limiter.is_allowed(client_ip, endpoint, "10/minute")
        
        # 11th request should be blocked
        is_allowed, retry_after = limiter.is_allowed(
            client_ip, endpoint, "10/minute"
        )
        assert is_allowed is False
        assert retry_after > 0
    
    def test_rate_limit_resets_after_window(self):
        """Test that rate limit resets after time window."""
        limiter = SimpleRateLimiter()
        client_ip = "127.0.0.1"
        endpoint = "/api/analyze/color"
        
        # Make requests at limit
        for i in range(10):
            limiter.is_allowed(client_ip, endpoint, "10/minute")
        
        # Manually clean up old entries (simulating time passage)
        current_time = time.time()
        # Set all requests to be old
        limiter.requests[client_ip] = [
            (current_time - 70, endpoint)  # 70 seconds ago
        ]
        limiter._cleanup_old_entries()
        
        # Now request should be allowed again
        is_allowed, retry_after = limiter.is_allowed(
            client_ip, endpoint, "10/minute"
        )
        assert is_allowed is True
    
    def test_different_endpoints_separate_limits(self):
        """Test that different endpoints have separate rate limits."""
        limiter = SimpleRateLimiter()
        client_ip = "127.0.0.1"
        
        # Exhaust limit for one endpoint
        for i in range(10):
            limiter.is_allowed(client_ip, "/api/analyze/color", "10/minute")
        
        # Other endpoint should still be available
        is_allowed, _ = limiter.is_allowed(
            client_ip, "/api/try-on/generate", "5/minute"
        )
        assert is_allowed is True
    
    def test_different_clients_separate_limits(self):
        """Test that different clients have separate rate limits."""
        limiter = SimpleRateLimiter()
        
        # Exhaust limit for one client
        for i in range(10):
            limiter.is_allowed("127.0.0.1", "/api/analyze/color", "10/minute")
        
        # Other client should still be available
        is_allowed, _ = limiter.is_allowed(
            "192.168.1.1", "/api/analyze/color", "10/minute"
        )
        assert is_allowed is True


class TestGetRemoteAddress:
    """Tests for get_remote_address function."""
    
    def test_get_remote_address_from_client(self):
        """Test getting IP from request.client."""
        request = Mock()
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {}
        
        ip = get_remote_address(request)
        assert ip == "127.0.0.1"
    
    def test_get_remote_address_from_forwarded_for(self):
        """Test getting IP from X-Forwarded-For header."""
        request = Mock()
        request.client = None
        request.headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        
        ip = get_remote_address(request)
        assert ip == "192.168.1.1"
    
    def test_get_remote_address_from_real_ip(self):
        """Test getting IP from X-Real-IP header."""
        request = Mock()
        request.client = None
        request.headers = {"X-Real-IP": "192.168.1.1"}
        
        ip = get_remote_address(request)
        assert ip == "192.168.1.1"
    
    def test_get_remote_address_unknown(self):
        """Test getting 'unknown' when no IP available."""
        request = Mock()
        request.client = None
        request.headers = {}
        
        ip = get_remote_address(request)
        assert ip == "unknown"

