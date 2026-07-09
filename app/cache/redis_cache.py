import json

from redis.asyncio import Redis

from app.core.config import RedisConfig, load_redis_config


class RedisCache:
    def __init__(self, redis_url: str):
        """Store Redis connection settings."""
        self.redis_url = redis_url
        self._client = Redis.from_url(redis_url, decode_responses=True)

    async def set_snapshot(self, user_id: int, payload: dict):
        """Save latest GSI snapshot for user."""
        # Store the raw snapshot as JSON because GSI payload structure can grow.
        await self._client.set(f'gsi:snapshot:{user_id}', json.dumps(payload))

    async def get_snapshot(self, user_id: int):
        """Return latest GSI snapshot for user."""
        snapshot = await self._client.get(f'gsi:snapshot:{user_id}')
        if snapshot is None:
            return None
        return json.loads(snapshot)

    async def set_active_match(self, user_id: int, match_id: int):
        """Save active match id for user."""
        # Keep the current match separate from the large snapshot payload.
        await self._client.set(f'gsi:active_match:{user_id}', match_id)

    async def get_active_match(self, user_id: int):
        """Return active match id for user."""
        match_id = await self._client.get(f'gsi:active_match:{user_id}')
        if match_id is None:
            return None
        return int(match_id)

    async def close(self):
        """Close Redis client connection."""
        await self._client.aclose()


redis_config: RedisConfig = load_redis_config()
redis_cache = RedisCache(redis_config.redis_url)
