import json
import functools
import redis
from datetime import timedelta, datetime
import logging
import time
import os
import socket

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Determine if Redis should be enabled
REDIS_ENABLED = os.environ.get('ENABLE_REDIS', 'true').lower() == 'true'

# Get Redis host from environment or default to localhost
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

# Initialize Redis client with error handling
REDIS_AVAILABLE = False
if REDIS_ENABLED:
    try:
        # Try to detect if running in WSL
        hostname = socket.gethostname()
        is_wsl = "WSL" in hostname or "wsl" in hostname or os.path.exists("/proc/sys/fs/binfmt_misc/WSLInterop")
        
        if is_wsl:
            logger.info(f"WSL environment detected, using '{REDIS_HOST}:{REDIS_PORT}' for Redis")
        
        redis_client = redis.Redis(
            host=REDIS_HOST, 
            port=REDIS_PORT, 
            db=0, 
            decode_responses=True, 
            socket_timeout=2,
            socket_connect_timeout=2
        )
        redis_client.ping()  # Test connection
        REDIS_AVAILABLE = True
        logger.info(f"Redis connection established to {REDIS_HOST}:{REDIS_PORT}")
    except (redis.ConnectionError, redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
        logger.warning(f"Redis connection failed: {e}. Caching will be disabled.")
else:
    logger.info("Redis is disabled by configuration")

# Simple in-memory cache for fallback when Redis is not available
memory_cache = {}
memory_cache_expiry = {}

# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def cache_response(prefix, expire=300):
    """
    Decorator to cache API responses in memory.
    
    Args:
        prefix (str): Prefix for the cache key
        expire (int): Cache expiration time in seconds (default: 5 minutes)
    
    Returns:
        Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Generate a cache key from the function arguments
                key_parts = [prefix]
                # Add class name if it's a method in a class
                if args and hasattr(args[0], '__class__'):
                    key_parts.append(args[0].__class__.__name__)
                
                # Add function arguments to the key
                for arg in args[1:]:
                    if isinstance(arg, (str, int, float, bool)):
                        key_parts.append(str(arg))
                
                # Add keyword arguments to the key
                for k, v in sorted(kwargs.items()):
                    if isinstance(v, (str, int, float, bool)):
                        key_parts.append(f"{k}:{v}")
                
                cache_key = ":".join(key_parts)
                
                # If Redis is available, try Redis first
                if REDIS_AVAILABLE:
                    try:
                        cached_data = redis_client.get(cache_key)
                        if cached_data:
                            logger.debug(f"Redis cache hit for {cache_key}")
                            return json.loads(cached_data)
                    except:
                        # If any Redis error, silently fallback to memory cache
                        pass
                
                # Try memory cache
                current_time = time.time()
                if cache_key in memory_cache and memory_cache_expiry.get(cache_key, 0) > current_time:
                    logger.debug(f"Memory cache hit for {cache_key}")
                    return memory_cache[cache_key]
                
                # Cache miss - call the function
                result = func(*args, **kwargs)
                
                # Only cache successful responses
                if isinstance(result, tuple) and len(result) == 2 and result[1] == 200:
                    # Try to cache in Redis first
                    if REDIS_AVAILABLE:
                        try:
                            redis_client.setex(
                                name=cache_key,
                                time=expire,
                                value=json.dumps(result[0], cls=DateTimeEncoder)
                            )
                        except:
                            # Silently fallback to memory cache on error
                            pass
                    
                    # Cache in memory regardless
                    memory_cache[cache_key] = result
                    memory_cache_expiry[cache_key] = current_time + expire
                    
                    # Simple memory cleanup
                    if len(memory_cache) > 1000:
                        for k in list(memory_cache_expiry.keys()):
                            if memory_cache_expiry[k] <= current_time:
                                memory_cache.pop(k, None)
                                memory_cache_expiry.pop(k, None)
                
                return result
            except Exception as e:
                # On any error, just call the original function
                logger.error(f"Cache error, bypassing cache: {e}")
                return func(*args, **kwargs)
        
        return wrapper
    
    return decorator

def invalidate_cache_prefix(prefix):
    """
    Invalidate all cache entries with the given prefix
    
    Args:
        prefix (str): Prefix of the cache keys to invalidate
    """
    # Clear memory cache entries
    keys_to_remove = []
    for key in memory_cache.keys():
        if key.startswith(prefix):
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        memory_cache.pop(key, None)
        memory_cache_expiry.pop(key, None)
    
    logger.debug(f"Invalidated {len(keys_to_remove)} memory cache entries with prefix '{prefix}'")
    
    # Clear Redis cache entries if available
    if REDIS_AVAILABLE:
        try:
            redis_keys = redis_client.keys(f"{prefix}*")
            if redis_keys:
                redis_client.delete(*redis_keys)
                logger.debug(f"Invalidated {len(redis_keys)} Redis cache entries with prefix '{prefix}'")
        except Exception as e:
            logger.warning(f"Error invalidating Redis cache: {e}")

def get_cache_stats():
    """
    Get cache statistics
    
    Returns:
        dict: Dictionary with cache statistics
    """
    stats = {
        'memory_cache': {
            'size': len(memory_cache),
            'keys': list(memory_cache.keys())[:10]  # First 10 keys only
        }
    }
    
    if REDIS_AVAILABLE:
        try:
            redis_info = redis_client.info()
            stats['redis'] = {
                'connected': True,
                'used_memory': redis_info.get('used_memory_human', 'N/A'),
                'connected_clients': redis_info.get('connected_clients', 'N/A'),
                'uptime_in_days': redis_info.get('uptime_in_days', 'N/A')
            }
        except Exception as e:
            stats['redis'] = {
                'connected': False,
                'error': str(e)
            }
    else:
        stats['redis'] = {
            'connected': False
        }
    
    return stats 