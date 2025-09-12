"""
Redis connection and caching utilities
"""

import json
import hashlib
from typing import Any, Optional, Union
import redis.asyncio as redis
import logging

from src.core.config import settings

logger = logging.getLogger(__name__)

# Global Redis connection pool
redis_pool: Optional[redis.ConnectionPool] = None
redis_client: Optional[redis.Redis] = None


async def init_redis() -> None:
    """Initialize Redis connection pool"""
    global redis_pool, redis_client
    
    try:
        redis_pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=True
        )
        redis_client = redis.Redis(connection_pool=redis_pool)
        
        # Test connection
        await redis_client.ping()
        logger.info("Redis connection established successfully")
        
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise


async def close_redis() -> None:
    """Close Redis connections"""
    global redis_pool, redis_client
    
    if redis_client:
        await redis_client.close()
    if redis_pool:
        await redis_pool.disconnect()
    
    logger.info("Redis connections closed")


def get_redis() -> redis.Redis:
    """Get Redis client instance"""
    if redis_client is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return redis_client


class CacheManager:
    """Redis-based cache manager with semantic caching capabilities"""
    
    def __init__(self):
        self.redis = get_redis()
        self.default_ttl = settings.CACHE_TTL
    
    def _generate_cache_key(self, prefix: str, data: Union[str, dict]) -> str:
        """Generate a cache key from data"""
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        
        # Create hash of the data for consistent key generation
        hash_object = hashlib.sha256(data.encode())
        hash_hex = hash_object.hexdigest()[:16]  # Use first 16 chars
        
        return f"{prefix}:{hash_hex}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value, default=str)
            await self.redis.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            result = await self.redis.delete(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            result = await self.redis.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def get_semantic_cache(self, prompt: str, model: str) -> Optional[dict]:
        """Get cached response for similar prompts using semantic similarity"""
        if not settings.CACHE_ENABLED:
            return None
        
        cache_key = self._generate_cache_key("semantic", f"{model}:{prompt}")
        return await self.get(cache_key)
    
    async def set_semantic_cache(self, prompt: str, model: str, response: dict, ttl: Optional[int] = None) -> bool:
        """Cache response for semantic similarity matching"""
        if not settings.CACHE_ENABLED:
            return False
        
        cache_key = self._generate_cache_key("semantic", f"{model}:{prompt}")
        return await self.set(cache_key, response, ttl)


# Global cache manager instance
cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get cache manager instance"""
    global cache_manager
    if cache_manager is None:
        cache_manager = CacheManager()
    return cache_manager

