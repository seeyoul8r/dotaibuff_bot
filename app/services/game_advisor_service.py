import json
import time
import uuid

from google import genai
from google.genai import types
from pydantic import BaseModel

from app.ai.prompts import GAME_ADVISOR_PROMPT
from app.bot.messages import mes_user
from app.cache.redis_cache import redis_cache
from app.core.config import AIConfig, LoggingConfig, load_ai_config, load_logging_config
from app.repositories.ai_request_repository import ai_request_repository
from app.services.dota_data_service import dota_data_service


class GameAdvice(BaseModel):
    """Structured Dota game advice."""
    macro_gaming: str
    build: str
    micro_gaming: str


class GameAdvisorService:
    def __init__(self):
        """Store AI advisor configuration."""
        self.prompt = GAME_ADVISOR_PROMPT
        self.config: AIConfig = load_ai_config()
        self.logging_config: LoggingConfig = load_logging_config()
        # Reuse one async Gemini client and its HTTP connections for all advice requests.
        self.client = genai.Client(api_key=self.config.api_key).aio
        # Keep cooldowns in the current bot process, matching the existing manager pattern.
        self._cooldowns = {}

    async def build_prompt(self, user_id: int, lang: str):
        """Build prompt from match state and relevant Dota data."""
        match_id = await redis_cache.get_active_match(user_id)
        match_state = await redis_cache.get_match_state(user_id, match_id)
        dota_data = dota_data_service.get_data()

        hero_names = self.get_roster_hero_names(match_state)
        item_names = {item['name'] for item in match_state['items'].values()}
        item_mechanics = await dota_data_service.get_item_mechanics(item_names)

        # Only the local hero's counters against the current enemy lineup are relevant.
        local_hero_name = match_state['hero'].get('name')
        local_team_name = match_state['player'].get('team_name')
        opponent_team_name = {'radiant': 'dire', 'dire': 'radiant'}.get(local_team_name)
        enemy_hero_names = set(match_state[opponent_team_name]['heroes']) if opponent_team_name else set()
        allied_hero_names = set(match_state[local_team_name]['heroes']) if local_team_name in ('radiant', 'dire') else set()
        local_hero_counters = dota_data['hero_counters'].get(local_hero_name, {})
        relevant_counters = {
            enemy_hero_name: local_hero_counters[enemy_hero_name]
            for enemy_hero_name in enemy_hero_names
            if enemy_hero_name in local_hero_counters
        }

        # Send only match-relevant mechanics and avoid lore or unrelated heroes.
        dota_context = {
            'updated_at': dota_data['updated_at'],
            'patch': dota_data['patch'],
            'hero_mechanics': {
                hero_name: self.compact_hero_mechanics(
                    dota_data['hero_mechanics'][hero_name],
                    self.get_hero_mechanics_scope(hero_name, local_hero_name, allied_hero_names, enemy_hero_names)
                )
                for hero_name in hero_names
                if hero_name in dota_data['hero_mechanics']
            },
            'local_items': {
                item_name: self.compact_ability_or_item(item_mechanics[item_name])
                for item_name in item_names
                if item_name in item_mechanics
            },
            'hero_win_rates': {
                hero_name: dota_data['hero_win_rates'][hero_name]
                for hero_name in hero_names
                if hero_name in dota_data['hero_win_rates']
            },
            'local_hero_counters': relevant_counters,
            'local_hero_builds': dota_data['hero_builds'].get(local_hero_name, {})
        }
        return {
            'language': 'Russian' if lang == 'ru' else 'English',
            'match_state': self.compact_match_state(match_state),
            'dota_context': dota_context
        }

    def compact_match_state(self, match_state: dict):
        """Return compact match state for AI prompt."""
        return self.remove_empty_state_values({
            'match_id': match_state.get('match_id'),
            'game_state': match_state.get('game_state'),
            'clock_time': match_state.get('clock_time'),
            'radiant_score': match_state.get('radiant_score'),
            'dire_score': match_state.get('dire_score'),
            'daytime': match_state.get('daytime'),
            'paused': match_state.get('paused'),
            'win_team': match_state.get('win_team'),
            'player': self.compact_player(match_state.get('player', {})),
            'hero': self.compact_local_hero(match_state.get('hero', {})),
            'abilities': self.compact_match_abilities(match_state.get('abilities', {})),
            'items': self.compact_match_items(match_state.get('items', {})),
            'buildings': match_state.get('buildings', {}),
            'radiant': self.compact_team(match_state.get('radiant', {})),
            'dire': self.compact_team(match_state.get('dire', {})),
            'enemy_positions': self.compact_enemy_positions(match_state)
        })

    def compact_player(self, player: dict):
        """Return compact local player state."""
        return self.remove_empty_state_values({
            'team_name': player.get('team_name'),
            'gold': player.get('gold'),
            'gold_reliable': player.get('gold_reliable'),
            'gold_unreliable': player.get('gold_unreliable'),
            'kills': player.get('kills'),
            'deaths': player.get('deaths'),
            'assists': player.get('assists'),
            'last_hits': player.get('last_hits'),
            'denies': player.get('denies'),
            'kill_streak': player.get('kill_streak')
        })

    def compact_local_hero(self, hero: dict):
        """Return compact local hero state."""
        return self.remove_empty_state_values({
            'name': hero.get('name'),
            'level': hero.get('level'),
            'alive': hero.get('alive'),
            'respawn_seconds': hero.get('respawn_seconds'),
            'health': hero.get('health'),
            'max_health': hero.get('max_health'),
            'mana': hero.get('mana'),
            'max_mana': hero.get('max_mana'),
            'has_debuff': hero.get('has_debuff'),
            'selected_unit': hero.get('selected_unit')
        })

    def compact_match_abilities(self, abilities: dict):
        """Return compact current ability state."""
        return {
            slot: self.remove_empty_state_values({
                'name': ability.get('name'),
                'level': ability.get('level'),
                'can_cast': ability.get('can_cast'),
                'passive': ability.get('passive'),
                'cooldown': ability.get('cooldown'),
                'ultimate': ability.get('ultimate')
            })
            for slot, ability in abilities.items()
        }

    def compact_match_items(self, items: dict):
        """Return compact current item state."""
        return {
            slot: self.remove_empty_state_values({
                'name': item.get('name'),
                'can_cast': item.get('can_cast'),
                'cooldown': item.get('cooldown'),
                'charges': item.get('charges'),
                'purchaser': item.get('purchaser')
            })
            for slot, item in items.items()
        }

    def compact_team(self, team: dict):
        """Return compact team roster state."""
        return {
            'heroes': list(team.get('heroes', {}))
        }

    def compact_enemy_positions(self, match_state: dict):
        """Return compact locked enemy visibility state."""
        player_team_name = match_state.get('player', {}).get('team_name')
        opponent_team_name = {'radiant': 'dire', 'dire': 'radiant'}.get(player_team_name)
        if opponent_team_name is None:
            return {}

        current_game_time = match_state.get('clock_time')
        enemy_positions = {}
        for hero_name, hero_state in match_state[opponent_team_name]['heroes'].items():
            last_seen_game_time = hero_state.get('last_seen_game_time')
            seen_seconds_ago = None
            if isinstance(current_game_time, (int, float)) and isinstance(last_seen_game_time, (int, float)):
                # Use game clock delta so advice can reason about map absence during the current match.
                seen_seconds_ago = max(0, int(current_game_time - last_seen_game_time))
            enemy_positions[hero_name] = self.remove_empty_state_values({
                'visible': hero_state.get('visible', False),
                'last_seen_location': hero_state.get('last_seen_location', 'unknown'),
                'last_seen_game_time': last_seen_game_time,
                'seen_seconds_ago': seen_seconds_ago,
                'last_seen_position': hero_state.get('last_seen_position')
            })
        return enemy_positions

    def get_hero_mechanics_scope(
            self, hero_name: str, local_hero_name: str | None, allied_hero_names: set, enemy_hero_names: set):
        """Return mechanics detail scope for a match hero."""
        if hero_name == local_hero_name:
            return 'local'
        if hero_name in enemy_hero_names:
            return 'enemy'
        if hero_name in allied_hero_names:
            return 'ally'
        return 'ally'

    def compact_hero_mechanics(self, hero_mechanics: dict, scope: str):
        """Return compact hero mechanics for AI prompt."""
        compact = {
            'name': hero_mechanics.get('name'),
            'name_loc': hero_mechanics.get('name_loc'),
            'abilities': [
                self.compact_ability_or_item(ability)
                for ability in hero_mechanics.get('abilities', [])
            ],
            'shard': [
                self.compact_ability_or_item(ability)
                for ability in hero_mechanics.get('shard', [])
            ],
            'scepter': [
                self.compact_ability_or_item(ability)
                for ability in hero_mechanics.get('scepter', [])
            ]
        }
        if scope == 'local':
            # Keep local talents because build advice is only for the user's hero.
            compact['talents'] = [
                self.compact_ability_or_item(talent)
                for talent in hero_mechanics.get('talents', [])
            ]
            compact['facets'] = hero_mechanics.get('facets', [])
        return self.remove_empty_values(compact)

    def compact_ability_or_item(self, ability: dict):
        """Return compact ability or item mechanics."""
        compact = {
            'name': ability.get('name'),
            'name_loc': ability.get('name_loc'),
            'desc_loc': ability.get('desc_loc'),
            'shard_loc': ability.get('shard_loc'),
            'scepter_loc': ability.get('scepter_loc'),
            'behavior': ability.get('behavior'),
            'damage': ability.get('damage'),
            'immunity': ability.get('immunity'),
            'dispellable': ability.get('dispellable'),
            'cast_ranges': ability.get('cast_ranges'),
            'cooldowns': ability.get('cooldowns'),
            'durations': ability.get('durations'),
            'damages': ability.get('damages'),
            'mana_costs': ability.get('mana_costs'),
            'item_cost': ability.get('item_cost'),
            'special_values': self.compact_special_values(ability.get('special_values', [])),
            'ability_is_innate': ability.get('ability_is_innate')
        }
        return self.remove_empty_values(compact)

    def compact_special_values(self, special_values: list):
        """Return compact non-empty special values."""
        compact_values = []
        for special_value in special_values:
            compact_value = {
                'name': special_value.get('name'),
                'heading_loc': special_value.get('heading_loc'),
                'values_float': special_value.get('values_float'),
                'values_shard': special_value.get('values_shard'),
                'values_scepter': special_value.get('values_scepter'),
                'facet_bonus': special_value.get('facet_bonus')
            }
            # Keep only values that can affect the model's fight or build reasoning.
            compact_values.append(self.remove_empty_values(compact_value))
        return [value for value in compact_values if value]

    def remove_empty_values(self, value: dict):
        """Return dict without empty values."""
        return {
            key: item
            for key, item in value.items()
            if item not in (None, [], {}, False)
        }

    def remove_empty_state_values(self, value: dict):
        """Return state dict without empty values."""
        return {
            key: item
            for key, item in value.items()
            if item not in (None, [], {})
        }

    def get_roster_hero_names(self, match_state: dict):
        """Return known match roster hero names."""
        radiant_heroes = set(match_state['radiant']['heroes'])
        dire_heroes = set(match_state['dire']['heroes'])
        if len(radiant_heroes) == 5 and len(dire_heroes) == 5:
            return radiant_heroes | dire_heroes
        return radiant_heroes | dire_heroes

    async def request_advice(self, user_id: int, lang: str):
        """Request structured match advice from Gemini."""
        prompt_data = await self.build_prompt(user_id, lang)
        contents = json.dumps(prompt_data, ensure_ascii=False)
        response_mime_type = 'application/json'
        response_schema = GameAdvice.model_json_schema()
        request_id = uuid.uuid4().hex
        if self.logging_config.log_requests:
            # Persist the exact request fields before sending them to Gemini.
            await ai_request_repository.create_request(
                request_id=request_id,
                user_id=user_id,
                match_id=prompt_data['match_state'].get('match_id'),
                request=contents,
                model=self.config.model,
                system_instruction=self.prompt,
                response_mime_type=response_mime_type,
                response_schema=json.dumps(response_schema, ensure_ascii=False),
                thinking_level=self.config.thinking_level
            )
        try:
            # Parse schema-constrained output directly without splitting free-form model text.
            response = await self.client.models.generate_content(
                model=self.config.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=self.prompt,
                    response_mime_type=response_mime_type,
                    response_schema=GameAdvice,
                    thinking_config=types.ThinkingConfig(thinking_level=self.config.thinking_level)
                )
            )
            advice = response.parsed
            if self.logging_config.log_requests:
                # Store the parsed structured response in the same request row.
                await ai_request_repository.save_response(
                    request_id,
                    json.dumps(advice.model_dump(), ensure_ascii=False)
                )
            return advice
        except Exception as error:
            if self.logging_config.log_requests:
                # Store failed Gemini request status before passing the error to the handler.
                await ai_request_repository.save_error(request_id, str(error))
            raise

    def is_on_cooldown(self, user_id: int):
        """Return remaining advice cooldown seconds."""
        current_time = time.time()
        last_request = self._cooldowns.get(user_id, 0)
        if current_time - last_request < self.config.advice_cooldown:
            return int(self.config.advice_cooldown - (current_time - last_request))
        return 0

    def set_cooldown(self, user_id: int):
        """Set advice cooldown for user."""
        self._cooldowns[user_id] = time.time()

    def reload_config(self):
        """Reload AI config from environment."""
        self.config = load_ai_config()
        # Clear old cooldown timestamps so the new limit applies immediately.
        self._cooldowns = {}

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
