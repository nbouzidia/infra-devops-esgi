"""
Prometheus instrumentation middleware for Django.
Records HTTP request metrics: count, duration, and errors.
"""

import time
from prometheus_client import Counter, Histogram

# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0)
)


class PrometheusMiddleware:
    """Middleware to track HTTP metrics for Prometheus."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Start timer
        start_time = time.time()
        
        # Get endpoint path (simplified)
        endpoint = request.path.split('/')[1] or 'root'
        
        try:
            # Process request
            response = self.get_response(request)
            status = response.status_code
        except Exception as e:
            # Record error and re-raise
            status = 500
            raise
        finally:
            # Record metrics
            duration = time.time() - start_time
            http_requests_total.labels(
                method=request.method,
                endpoint=endpoint,
                status=status
            ).inc()
            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)
        
        return response
