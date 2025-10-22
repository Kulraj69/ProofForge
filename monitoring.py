import time
import psutil
from typing import Dict, Any
from datetime import datetime
from functools import wraps

class PerformanceMonitor:
    """Performance monitoring for API endpoints"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {
            'request_count': 0,
            'total_response_time': 0,
            'average_response_time': 0,
            'error_count': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        self.start_time = time.time()
    
    def record_request(self, response_time: float, success: bool = True):
        """Record request metrics"""
        self.metrics['request_count'] += 1
        self.metrics['total_response_time'] += response_time
        self.metrics['average_response_time'] = (
            self.metrics['total_response_time'] / self.metrics['request_count']
        )
        
        if not success:
            self.metrics['error_count'] += 1
    
    def record_cache_hit(self):
        """Record cache hit"""
        self.metrics['cache_hits'] += 1
    
    def record_cache_miss(self):
        """Record cache miss"""
        self.metrics['cache_misses'] += 1
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'uptime': time.time() - self.start_time
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all performance metrics"""
        return {
            **self.metrics,
            'system': self.get_system_metrics(),
            'timestamp': datetime.now().isoformat()
        }

# Global performance monitor
performance_monitor = PerformanceMonitor()

def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        success = True
        
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            success = False
            raise e
        finally:
            response_time = time.time() - start_time
            performance_monitor.record_request(response_time, success)
    
    return wrapper

def get_performance_metrics() -> Dict[str, Any]:
    """Get current performance metrics"""
    return performance_monitor.get_metrics()
