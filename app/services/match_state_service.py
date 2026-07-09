from datetime import UTC, datetime

from app.cache.redis_cache import redis_cache


class MatchStateService:
    async def update_match_state(self, user_id: int, match_id: int, payload: dict):
        """Update accumulated match state from GSI snapshot."""
        match_state = await self.get_match_state(user_id, match_id)
        now = datetime.now(UTC).isoformat()
        map_data = payload.get('map', {})
        # Keep current game timing fields on every snapshot.
        match_state['game_state'] = map_data.get('game_state')
        match_state['game_time'] = map_data.get('game_time')
        match_state['updated_at'] = now

        player_hero = self.extract_player_hero(payload)
        if player_hero:
            self.apply_hero(match_state, player_hero['hero_name'], player_hero['team_name'], 'hero', now)

        for minimap_hero in self.extract_minimap_heroes(payload):
            self.apply_hero(
                match_state,
                minimap_hero['hero_name'],
                minimap_hero['team_name'],
                'minimap',
                now
            )

        await redis_cache.set_match_state(user_id, match_id, match_state)
        print(
            f'GSI match state updated: user_id={user_id}, match_id={match_id}, '
            f'radiant={len(match_state["radiant"]["heroes"])}, '
            f'dire={len(match_state["dire"]["heroes"])}, '
            f'unknown={len(match_state["unknown_heroes"])}'
        )

    async def get_match_state(self, user_id: int, match_id: int):
        """Return current match state or create empty one."""
        match_state = await redis_cache.get_match_state(user_id, match_id)
        if match_state is not None:
            return match_state
        return {
            'user_id': user_id,
            'match_id': match_id,
            'game_state': None,
            'game_time': None,
            'radiant': {'heroes': {}},
            'dire': {'heroes': {}},
            'unknown_heroes': {},
            'created_at': datetime.now(UTC).isoformat(),
            'updated_at': datetime.now(UTC).isoformat()
        }

    def extract_player_hero(self, payload: dict):
        """Extract local player hero from GSI snapshot."""
        hero_name = payload.get('hero', {}).get('name')
        team_name = payload.get('player', {}).get('team_name')
        if hero_name is None:
            return None
        return {
            'hero_name': hero_name,
            'team_name': team_name
        }

    def extract_minimap_heroes(self, payload: dict):
        """Extract hero unit names from minimap data."""
        heroes = []
        minimap = payload.get('minimap', {})
        for minimap_object in minimap.values():
            hero_name = minimap_object.get('unitname')
            if not isinstance(hero_name, str) or not hero_name.startswith('npc_dota_hero_'):
                continue
            heroes.append({
                'hero_name': hero_name,
                'team_name': self.get_team_name(minimap_object.get('team'))
            })
        return heroes

    def apply_hero(self, match_state: dict, hero_name: str, team_name: str | None, source: str, now: str):
        """Apply hero to accumulated match state."""
        team_key = team_name if team_name in ('radiant', 'dire') else 'unknown_heroes'
        previous_hero_state = self.pop_hero(match_state, hero_name)
        heroes = match_state[team_key]['heroes'] if team_key in ('radiant', 'dire') else match_state[team_key]
        hero_state = previous_hero_state or {
            'team': team_name,
            'sources': [],
            'first_seen_at': now,
            'last_seen_at': now
        }
        if source not in hero_state['sources']:
            # Track every source that confirmed this hero.
            hero_state['sources'].append(source)
        hero_state['team'] = team_name
        hero_state['last_seen_at'] = now
        heroes[hero_name] = hero_state

    def pop_hero(self, match_state: dict, hero_name: str):
        """Remove hero from current match state buckets."""
        # Keep one current team bucket per hero when later snapshots update team data.
        hero_state = match_state['radiant']['heroes'].pop(hero_name, None)
        if hero_state is not None:
            return hero_state
        hero_state = match_state['dire']['heroes'].pop(hero_name, None)
        if hero_state is not None:
            return hero_state
        return match_state['unknown_heroes'].pop(hero_name, None)

    def get_team_name(self, team_id: int | None):
        """Return team name by GSI team id."""
        if team_id == 2:
            return 'radiant'
        if team_id == 3:
            return 'dire'
        return None


match_state_service = MatchStateService()
