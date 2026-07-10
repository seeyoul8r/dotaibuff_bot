from app.cache.redis_cache import redis_cache
from app.bot.messages import mes_user
from app.services.dota_data_service import dota_data_service


class GameAdvisorService:
    def __init__(self):
        """Store base AI advisor prompt."""
        self.prompt = 'Analyze current Dota 2 game snapshot and give concise advice.'

    async def build_prompt(self, user_id: int):
        """Build prompt from match state and relevant Dota data."""
        match_id = await redis_cache.get_active_match(user_id)
        match_state = await redis_cache.get_match_state(user_id, match_id)
        dota_data = dota_data_service.get_data()

        hero_names = set(match_state['radiant']['heroes']) | set(match_state['dire']['heroes'])
        hero_names |= set(match_state['unknown_heroes'])
        item_names = {item['name'] for item in match_state['items'].values()}
        ability_names = {ability['name'] for ability in match_state['abilities'].values()}

        # Send only match-relevant OpenDota records to the future AI client.
        dota_context = {
            'updated_at': dota_data['updated_at'],
            'patch': dota_data['patch'],
            'heroes': {
                hero_name: dota_data['heroes'][hero_name]
                for hero_name in hero_names
                if hero_name in dota_data['heroes']
            },
            'local_items': {
                item_name: dota_data['items'][item_name.removeprefix('item_')]
                for item_name in item_names
                if item_name.removeprefix('item_') in dota_data['items']
            },
            'local_abilities': {
                ability_name: dota_data['abilities'][ability_name]
                for ability_name in ability_names
                if ability_name in dota_data['abilities']
            }
        }
        return {
            'prompt': self.prompt,
            'match_state': match_state,
            'dota_context': dota_context
        }

    async def request_advice(self, user_id: int, lang: str):
        """Return current match state summary."""
        match_id = await redis_cache.get_active_match(user_id)
        if match_id is None:
            return mes_user[lang].snapshot_not_received
        match_state = await redis_cache.get_match_state(user_id, match_id)
        if match_state is None:
            return mes_user[lang].snapshot_not_received
        return self.format_snapshot(match_state, lang)

    def format_snapshot(self, match_state: dict, lang: str):
        """Format accumulated match state for user."""
        messages = mes_user[lang]
        player = match_state['player']
        hero = match_state['hero']
        abilities = match_state['abilities']
        items = match_state['items']

        # Build compact summary from normalized accumulated match data.
        lines = [
            messages.snapshot_title,
            '',
            f"{messages.match_label}: {match_state.get('match_id')}",
            f"{messages.game_state_label}: {match_state.get('game_state')}",
            f"{messages.time_label}: {match_state.get('clock_time')} {messages.seconds_label}",
            f"{messages.score_label}: {match_state.get('radiant_score')} / {match_state.get('dire_score')}",
            f"{messages.hero_label}: {hero.get('name')}",
            f"{messages.level_label}: {hero.get('level')}",
            f"{messages.hp_label}: {hero.get('health')} / {hero.get('max_health')}",
            f"{messages.mana_label}: {hero.get('mana')} / {hero.get('max_mana')}",
            f"{messages.gold_label}: {player.get('gold')}",
            f"{messages.kda_label}: {player.get('kills')} / {player.get('deaths')} / {player.get('assists')}",
            '',
            f'{messages.abilities_label}:'
        ]

        # Add learned abilities with level and cooldown information.
        for ability in abilities.values():
            if ability.get('name'):
                lines.append(
                    f"- {ability.get('name')}: {messages.ability_level_label} {ability.get('level')}, "
                    f"{messages.cooldown_label} {ability.get('cooldown')}"
                )

        lines.append('')
        lines.append(f'{messages.items_label}:')

        # Add filled item slots from the latest GSI snapshot.
        for item in items.values():
            if item.get('name'):
                lines.append(f"- {item.get('name')}")

        lines.append('')
        lines.append(f'{messages.radiant_label}:')
        for hero_name in match_state['radiant']['heroes']:
            lines.append(f'- {hero_name}')

        lines.append('')
        lines.append(f'{messages.dire_label}:')
        for hero_name in match_state['dire']['heroes']:
            lines.append(f'- {hero_name}')

        return '\n'.join(lines)


game_advisor_service = GameAdvisorService()
