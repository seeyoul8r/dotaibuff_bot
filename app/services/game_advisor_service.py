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
        """Return current snapshot summary."""
        snapshot = await redis_cache.get_snapshot(user_id)
        if snapshot is None:
            return 'GSI snapshot еще не получен.'
        return self.format_snapshot(snapshot)

    def format_snapshot(self, snapshot: dict):
        """Format latest GSI snapshot for user."""
        map_data = snapshot.get('map', {})
        player = snapshot.get('player', {})
        hero = snapshot.get('hero', {})
        abilities = snapshot.get('abilities', {})
        items = snapshot.get('items', {})

        # Build compact game summary from the main GSI blocks.
        lines = [
            'Текущий snapshot',
            '',
            f"Матч: {map_data.get('matchid')}",
            f"Время: {map_data.get('game_time')} сек",
            f"Герой: {hero.get('name')}",
            f"Уровень: {hero.get('level')}",
            f"HP: {hero.get('health')} / {hero.get('max_health')}",
            f"Mana: {hero.get('mana')} / {hero.get('max_mana')}",
            f"Gold: {player.get('gold')}",
            f"KDA: {player.get('kills')} / {player.get('deaths')} / {player.get('assists')}",
            '',
            'Abilities:'
        ]

        # Add learned abilities with level and cooldown information.
        for ability in abilities.values():
            if ability.get('name'):
                lines.append(
                    f"- {ability.get('name')}: level {ability.get('level')}, cooldown {ability.get('cooldown')}"
                )

        lines.append('')
        lines.append('Items:')

        # Add filled item slots from the latest GSI snapshot.
        for item in items.values():
            if item.get('name'):
                lines.append(f"- {item.get('name')}")

        return '\n'.join(lines)


game_advisor_service = GameAdvisorService()
