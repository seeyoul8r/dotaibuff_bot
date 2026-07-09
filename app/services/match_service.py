from app.cache.redis_cache import redis_cache


class MatchService:
    async def process_snapshot(self, user_id: int, payload: dict):
        """Save current GSI snapshot and active match."""
        match_id = self.get_match_id(payload)
        # Keep latest snapshot available for AI analysis requests.
        await redis_cache.set_snapshot(user_id, payload)
        if match_id is not None:
            # Update active match only when Dota sends match id.
            await redis_cache.set_active_match(user_id, match_id)

    def get_match_id(self, payload: dict):
        """Return match id from GSI payload."""
        return payload.get('map', {}).get('matchid')


match_service = MatchService()
