from app.cache.redis_cache import redis_cache
from app.bot.bot_instances import bot
from app.services.gsi_snapshot_log_service import gsi_snapshot_log_service
from app.services.match_state_service import match_state_service


class MatchService:
    async def process_snapshot(self, user_id: int, payload: dict):
        """Save current GSI snapshot and active match."""
        match_id = self.get_match_id(payload)
        # Write raw GSI data to JSONL for later match analysis.
        await gsi_snapshot_log_service.save_snapshot(user_id, match_id, payload)
        # Keep latest snapshot available for AI analysis requests.
        await redis_cache.set_snapshot(user_id, payload)
        if match_id is not None:
            await match_state_service.update_match_state(user_id, match_id, payload)
            notified_match_id = await redis_cache.get_match_started_notified(user_id)
            if notified_match_id != match_id:
                # Notify user only once for each new match id.
                await bot.send_message(user_id, text=f'Матч {match_id} начался.\nID матча: {match_id}')
                await redis_cache.set_match_started_notified(user_id, match_id)
            # Update active match only when Dota sends match id.
            await redis_cache.set_active_match(user_id, match_id)

    def get_match_id(self, payload: dict):
        """Return match id from GSI payload."""
        match_id = payload.get('map', {}).get('matchid')
        if match_id is None:
            return None
        return int(match_id)


match_service = MatchService()
