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

    async def set_match_started_notified(self, user_id: int, match_id: int):
        """Save notified match id for user."""
        # Store last notified match id to avoid repeated start messages.
        await self._client.set(f'gsi:match_started_notified:{user_id}', match_id)

    async def get_match_started_notified(self, user_id: int):
        """Return notified match id for user."""
        match_id = await self._client.get(f'gsi:match_started_notified:{user_id}')
        if match_id is None:
            return None
        return int(match_id)

    async def set_match_finished_notified(self, user_id: int, match_id: int):
        """Save finished match notification flag."""
        # Store one flag per user and match to avoid repeated post-game messages.
        await self._client.set(f'gsi:match_finished_notified:{user_id}:{match_id}', 1)

    async def get_match_finished_notified(self, user_id: int, match_id: int):
        """Return finished match notification flag."""
        notified = await self._client.get(f'gsi:match_finished_notified:{user_id}:{match_id}')
        return notified is not None

    async def set_match_state(self, user_id: int, match_id: int, state: dict):
        """Save accumulated match state."""
        # Store normalized match state separately from raw snapshots.
        await self._client.set(f'gsi:match_state:{user_id}:{match_id}', json.dumps(state))

    async def get_match_state(self, user_id: int, match_id: int):
        """Return accumulated match state."""
        state = await self._client.get(f'gsi:match_state:{user_id}:{match_id}')
        if state is None:
            return None
        return json.loads(state)

    async def clear_match_runtime(self, user_id: int, match_id: int):
        """Delete current match runtime data."""
        # Remove data used by AI recommendations after the match is finished.
        return await self._client.delete(
            f'gsi:snapshot:{user_id}',
            f'gsi:active_match:{user_id}',
            f'gsi:match_state:{user_id}:{match_id}'
        )

    async def clear_gsi_state(self):
        """Delete all GSI runtime keys."""
        keys = []
        async for key in self._client.scan_iter('gsi:*'):
            keys.append(key)
        if keys:
            # Clear only runtime GSI state, not unrelated Redis data.
            return await self._client.delete(*keys)
        return 0

    async def close(self):
        """Close Redis client connection."""
        await self._client.aclose()


redis_config: RedisConfig = load_redis_config()
redis_cache = RedisCache(redis_config.redis_url)
