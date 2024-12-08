# src/cache/cache_manager.py

from typing import Any, Optional
import aioredis
import json
import logging
from datetime import timedelta
from src.config.settings import settings

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Handles caching using Redis for improved performance.
    """
    
    def __init__(self):
        self.redis = None
        
    async def connect(self):
        """
        Establish connection to Redis.
        """
        try:
            self.redis = await aioredis.create_redis_pool(settings.REDIS_URL)
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise

    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache.
        """
        try:
            value = await self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: int = 3600  # 1 hour default
    ):
        """
        Store value in cache.
        """
        try:
            await self.redis.set(
                key,
                json.dumps(value),
                expire=expire
            )
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")

    async def close(self):
        """
        Close cache connections.
        """
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()