from datetime import UTC, datetime

from app.cache.redis_cache import redis_cache


class MatchStateService:
    async def update_match_state(self, user_id: int, match_id: int, payload: dict):
        """Update accumulated match state from GSI snapshot."""
        match_state = await self.get_match_state(user_id, match_id)
        now = datetime.now(UTC).isoformat()
        map_data = payload.get('map', {})
        # Update only fields present in the current GSI snapshot.
        for field in ('game_state', 'game_time', 'clock_time', 'radiant_score', 'dire_score',
                      'daytime', 'paused', 'win_team'):
            if field in map_data:
                match_state[field] = map_data[field]
        match_state['updated_at'] = now

        player = payload.get('player', {})
        hero = payload.get('hero', {})
        if player:
            match_state['player'].update(player)
        if hero:
            match_state['hero'].update(hero)

        # Keep current gameplay abilities and discard cosmetic actions.
        for slot, ability in payload.get('abilities', {}).items():
            ability_name = ability.get('name')
            if ability_name and not ability_name.startswith(('plus_', 'seasonal_')):
                match_state['abilities'][slot] = ability

        # Replace filled item slots and remove items that left a slot.
        for slot, item in payload.get('items', {}).items():
            if item.get('name') == 'empty':
                match_state['items'].pop(slot, None)
            elif item.get('name'):
                match_state['items'][slot] = item

        if payload.get('buildings'):
            match_state['buildings'].update(payload['buildings'])

        player_hero = self.extract_player_hero(payload)
        if player_hero:
            self.apply_hero(match_state, player_hero['hero_name'], player_hero['team_name'], 'hero', now)

        player_team_name = match_state['player'].get('team_name')
        minimap_heroes = self.extract_minimap_heroes(payload, player_team_name)
        # Apply reliable allied and visible-enemy markers before resolving plain circles.
        for minimap_hero in minimap_heroes:
            if minimap_hero['image'] == 'minimap_plaincircle':
                continue
            hero_state = self.apply_hero(
                match_state,
                minimap_hero['hero_name'],
                minimap_hero['team_name'],
                'minimap',
                now
            )
            # Keep the last reliable visible position for map-aware advice.
            hero_state['last_seen_position'] = minimap_hero['position']
            hero_state['last_seen_image'] = minimap_hero['image']

        if player_team_name in ('radiant', 'dire'):
            local_heroes = match_state[player_team_name]['heroes']
            plaincircle_heroes = {
                minimap_hero['hero_name']
                for minimap_hero in minimap_heroes
                if minimap_hero['image'] == 'minimap_plaincircle'
                and minimap_hero['hero_name'] not in local_heroes
            }
            if match_state['enemy_detection_ready']:
                opponent_team_name = 'dire' if player_team_name == 'radiant' else 'radiant'
                # Infer enemy roster only after the allied lineup baseline was confirmed.
                for hero_name in plaincircle_heroes:
                    self.apply_hero(
                        match_state,
                        hero_name,
                        opponent_team_name,
                        'minimap_plaincircle_inferred',
                        now
                    )
            elif len(local_heroes) == 5 and not plaincircle_heroes:
                # A clean five-allies snapshot separates live markers from stale draft markers.
                match_state['enemy_detection_ready'] = True

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
            'clock_time': None,
            'radiant_score': None,
            'dire_score': None,
            'daytime': None,
            'paused': None,
            'win_team': None,
            'player': {},
            'hero': {},
            'abilities': {},
            'items': {},
            'buildings': {},
            'radiant': {'heroes': {}},
            'dire': {'heroes': {}},
            'unknown_heroes': {},
            'enemy_detection_ready': False,
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

    def extract_minimap_heroes(self, payload: dict, player_team_name: str | None):
        """Extract hero unit names from minimap data."""
        heroes = []
        minimap = payload.get('minimap', {})
        for minimap_object in minimap.values():
            hero_name = minimap_object.get('unitname')
            if not isinstance(hero_name, str) or not hero_name.startswith('npc_dota_hero_'):
                continue
            image = minimap_object.get('image')
            if image in ('minimap_herocircle', 'minimap_herocircle_self', 'minimap_heroinvis'):
                team_name = player_team_name
            elif image == 'minimap_enemyicon' and player_team_name in ('radiant', 'dire'):
                team_name = 'dire' if player_team_name == 'radiant' else 'radiant'
            elif image == 'minimap_plaincircle':
                team_name = None
            else:
                # Ignore unrelated temporary minimap markers.
                continue
            heroes.append({
                'hero_name': hero_name,
                'team_name': team_name,
                'image': image,
                'position': {
                    'xpos': minimap_object.get('xpos'),
                    'ypos': minimap_object.get('ypos')
                }
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
        return hero_state

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
