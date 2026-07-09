from app.cache.redis_cache import redis_cache
from app.services.dota_state_service import dota_state_service


class GameAdvisorService:
    def __init__(self):
        """Store base AI advisor prompt."""
        self.prompt = 'Analyze current Dota 2 game snapshot and give concise advice.'

    async def build_prompt(self, user_id: int):
        """Build prompt from snapshot and Dota state."""
        snapshot = await redis_cache.get_snapshot(user_id)
        dota_state = await dota_state_service.get_current_state()
        # Combine live game data and external Dota state in one AI input.
        return {
            'prompt': self.prompt,
            'snapshot': snapshot,
            'dota_state': dota_state
        }

    async def request_advice(self, user_id: int):
        """Return AI advice request payload."""
        return await self.build_prompt(user_id)


game_advisor_service = GameAdvisorService()
