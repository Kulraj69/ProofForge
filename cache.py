import time
from typing import Dict, Any, Optional
from functools import lru_cache
import hashlib

class TTLCache:
    """Simple TTL cache for GitHub API responses"""
    
    def __init__(self, ttl_seconds: int = 300):  # 5 minutes default
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached value if not expired"""
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['data']
            else:
                # Remove expired entry
                del self.cache[key]
        return None
    
    def set(self, key: str, data: Dict[str, Any]) -> None:
        """Set cached value with timestamp"""
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def clear(self) -> None:
        """Clear all cached entries"""
        self.cache.clear()

# Global cache instance
github_cache = TTLCache(ttl_seconds=300)  # 5 minutes TTL

@lru_cache(maxsize=128)
def cached_parse_github_url(url: str) -> tuple[str, str]:
    """Cached GitHub URL parsing"""
    from urllib.parse import urlparse
    parsed = urlparse(str(url))
    path = parsed.path.strip('/')
    parts = path.split('/')
    if len(parts) >= 2:
        return parts[0], parts[1]
    else:
        raise ValueError("Invalid GitHub URL format")

def generate_cache_key(owner: str, repo: str) -> str:
    """Generate cache key for repository data"""
    return hashlib.md5(f"{owner}/{repo}".encode()).hexdigest()
