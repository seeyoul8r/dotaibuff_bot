import asyncio
import json
import logging
import time
import urllib.request
from urllib.parse import urlencode
from datetime import UTC, datetime

from app.core.config import StratzConfig, load_stratz_config


OPENDOTA_BASE_URL = 'https://api.opendota.com/api'
DOTA2_DATAFEED_BASE_URL = 'https://www.dota2.com/datafeed'
DOTA2_DATAFEED_LANGUAGE = 'english'
STRATZ_GRAPHQL_URL = 'https://api.stratz.com/graphql'
DOTA_DATA_UPDATE_INTERVAL = 60 * 60 * 24
logger = logging.getLogger(__name__)

# One combined query per hero keeps STRATZ calls at one per hero per update cycle.
STRATZ_HERO_QUERY = '''
query HeroStratzData($heroId: Short!) {
  heroStats {
    winGameVersion(heroIds: [$heroId], take: 1) {
      gameVersionId
      winCount
      matchCount
    }
    heroVsHeroMatchup(heroId: $heroId, take: 150) {
      advantage {
        vs { heroId2 synergy winRateHeroId1 matchCount }
      }
    }
    itemStartingPurchase(heroId: $heroId) {
      itemId
      wasGiven
      matchCount
      winsAverage
    }
    itemFullPurchase(heroId: $heroId) {
      itemId
      time
      matchCount
      winsAverage
    }
    abilityMinLevel(heroId: $heroId) {
      abilityId
      level
      matchCount
      winCount
    }
    abilityMaxLevel(heroId: $heroId) {
      abilityId
      level
      matchCount
      winCount
    }
    talent(heroId: $heroId) {
      abilityId
      matchCount
      winsAverage
    }
  }
}
'''


class DotaDataService:
    def __init__(self):
        """Create empty Dota data holder."""
        self.updated_at = None
        self.is_ready = False
        self.hero_stats = {}
        self.heroes = {}
        self.items = {}
        self.abilities = {}
        self.patches = []
        self.latest_patch = None
        self.patch_notes = {}
        self.datafeed_heroes = {}
        self.datafeed_items = {}
        self.hero_mechanics = {}
        self.item_mechanics = {}
        self.ability_ids = {}
        self.hero_win_rates = {}
        self.hero_counters = {}
        self.hero_builds = {}
        self.stratz_config: StratzConfig = load_stratz_config()
        self.admin_update_notifier = None

    async def start_daily_update(self):
        """Start daily Dota data update loop."""
        await self.update_data()
        while True:
            await asyncio.sleep(DOTA_DATA_UPDATE_INTERVAL)
            await self.update_data()

    async def update_data(self):
        """Update all collected Dota data."""
        started_at = time.monotonic()
        await self.notify_admins('Dota data update started.')
        try:
            logger.info('Dota data update started.')
            hero_stats = await self.fetch_opendota_json('/heroStats')
            heroes = await self.fetch_opendota_json('/constants/heroes')
            items = await self.fetch_opendota_json('/constants/items')
            abilities = await self.fetch_opendota_json('/constants/abilities')
            # /constants/abilities has no numeric id; ability_ids is the id->name lookup STRATZ ids need.
            ability_ids = await self.fetch_opendota_json('/constants/ability_ids')
            patches = await self.fetch_opendota_json('/constants/patch')
            logger.info(
                f'OpenDota data loaded: heroes={len(heroes)}, items={len(items)}, '
                f'abilities={len(abilities)}, ability_ids={len(ability_ids)}, '
                f'patch={patches[-1]["name"] if patches else None}'
            )
            datafeed_heroes = await self.fetch_dota2_datafeed_json('/herolist')
            datafeed_items = await self.fetch_dota2_datafeed_json('/itemlist')
            logger.info(
                f'Dota 2 datafeed lists loaded: '
                f'heroes={len(datafeed_heroes["result"]["data"]["heroes"])}, '
                f'items={len(datafeed_items["result"]["data"]["itemabilities"])}'
            )

            # Index heroes by the same names received from Dota GSI.
            self.hero_stats = {hero['name']: hero for hero in hero_stats}
            self.heroes = {
                hero['name']: {
                    'definition': hero,
                    'stats': self.hero_stats[hero['name']]
                }
                for hero in heroes.values()
            }
            self.items = items
            self.abilities = abilities
            self.ability_ids = ability_ids
            self.patches = patches
            self.latest_patch = patches[-1] if patches else None
            self.patch_notes = {}
            self.datafeed_heroes = {
                hero['name']: hero
                for hero in datafeed_heroes['result']['data']['heroes']
            }
            self.datafeed_items = {
                item['name']: item
                for item in datafeed_items['result']['data']['itemabilities']
            }
            self.hero_mechanics = await self.fetch_all_hero_mechanics()
            self.item_mechanics = {}
            self.hero_win_rates, self.hero_counters, self.hero_builds = await self.fetch_all_stratz_data()
            self.updated_at = datetime.now(UTC).isoformat()
            self.is_ready = True
            duration = time.monotonic() - started_at
            completed_message = (
                f'Dota data update completed in {duration:.1f} sec.\n'
                f'OpenDota: heroes={len(self.heroes)}, items={len(self.items)}, '
                f'abilities={len(self.abilities)}, patch={self.latest_patch["name"]}\n'
                f'Dota2 datafeed: hero_mechanics={len(self.hero_mechanics)}, '
                f'item_list={len(self.datafeed_items)}\n'
                f'STRATZ: hero_win_rates={len(self.hero_win_rates)}, hero_counters={len(self.hero_counters)}, '
                f'hero_builds={len(self.hero_builds)}'
            )
            logger.info(completed_message)
            await self.notify_admins(completed_message)
        except Exception as error:
            duration = time.monotonic() - started_at
            await self.notify_admins(f'Dota data update failed after {duration:.1f} sec.\n{error}')
            raise

    def get_data(self):
        """Return current collected Dota data."""
        return {
            'updated_at': self.updated_at,
            'is_ready': self.is_ready,
            'heroes': self.heroes,
            'items': self.items,
            'abilities': self.abilities,
            'datafeed_heroes': self.datafeed_heroes,
            'datafeed_items': self.datafeed_items,
            'hero_mechanics': self.hero_mechanics,
            'item_mechanics': self.item_mechanics,
            'hero_win_rates': self.hero_win_rates,
            'hero_counters': self.hero_counters,
            'hero_builds': self.hero_builds,
            'patches': self.patches,
            'patch': {
                'metadata': self.latest_patch,
                'notes': self.patch_notes
            }
        }

    async def fetch_opendota_json(self, path: str):
        """Fetch JSON data from OpenDota."""
        return await asyncio.to_thread(self.fetch_opendota_json_sync, path)

    def fetch_opendota_json_sync(self, path: str):
        """Fetch JSON data from OpenDota in blocking mode."""
        request = urllib.request.Request(
            f'{OPENDOTA_BASE_URL}{path}',
            headers={'User-Agent': 'DotAIBuffBot/0.1'}
        )
        # OpenDota rejects default urllib User-Agent with 403.
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))

    async def fetch_dota2_datafeed_json(self, path: str, params: dict | None = None):
        """Fetch JSON data from Dota 2 datafeed."""
        return await asyncio.to_thread(self.fetch_dota2_datafeed_json_sync, path, params)

    def fetch_dota2_datafeed_json_sync(self, path: str, params: dict | None = None):
        """Fetch Dota 2 datafeed JSON in blocking mode."""
        query_params = {'language': DOTA2_DATAFEED_LANGUAGE}
        if params:
            query_params.update(params)
        request = urllib.request.Request(
            f'{DOTA2_DATAFEED_BASE_URL}{path}?{urlencode(query_params)}',
            headers={'User-Agent': 'DotAIBuffBot/0.1'}
        )
        # Dota 2 datafeed contains current localized mechanics from dota2.com.
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))

    async def fetch_all_hero_mechanics(self):
        """Fetch mechanics for every listed hero."""
        hero_mechanics = {}
        heroes = list(self.datafeed_heroes.values())
        for index, hero in enumerate(heroes, start=1):
            hero_data = await self.fetch_dota2_datafeed_json('/herodata', {'hero_id': hero['id']})
            for hero_detail in hero_data['result']['data']['heroes']:
                # Keep mechanics indexed by GSI hero name for direct match_state lookup.
                hero_mechanics[hero_detail['name']] = self.normalize_hero_mechanics(hero_detail)
            if index % 25 == 0 or index == len(heroes):
                logger.info(f'Dota 2 hero mechanics loading: {index}/{len(heroes)}')
        return hero_mechanics

    async def get_item_mechanics(self, item_names: set[str]):
        """Return mechanics for requested item names."""
        for item_name in item_names:
            if item_name in self.item_mechanics or item_name not in self.datafeed_items:
                continue
            item_id = self.datafeed_items[item_name]['id']
            item_data = await self.fetch_dota2_datafeed_json('/itemdata', {'item_id': item_id})
            for item_detail in item_data['result']['data']['items']:
                # Cache only requested item data and avoid loading every item on startup.
                self.item_mechanics[item_detail['name']] = self.normalize_ability_or_item(item_detail)
                logger.info(f'Dota 2 item mechanics loaded: {item_detail["name"]}')
        return {
            item_name: self.item_mechanics[item_name]
            for item_name in item_names
            if item_name in self.item_mechanics
        }

    async def fetch_stratz_json(self, query: str, variables: dict):
        """Fetch JSON data from STRATZ GraphQL API."""
        return await asyncio.to_thread(self.fetch_stratz_json_sync, query, variables)

    def fetch_stratz_json_sync(self, query: str, variables: dict):
        """Fetch STRATZ GraphQL JSON in blocking mode."""
        body = json.dumps({'query': query, 'variables': variables}).encode('utf-8')
        request = urllib.request.Request(
            STRATZ_GRAPHQL_URL,
            data=body,
            headers={
                'User-Agent': 'DotAIBuffBot/0.1',
                'Content-Type': 'application/json',
                # The configured token already includes the required "Bearer " prefix.
                'Authorization': self.stratz_config.api_token
            }
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))

    async def fetch_all_stratz_data(self):
        """Fetch STRATZ win rate, counter, and build data for every hero."""
        hero_id_to_name = {hero['definition']['id']: gsi_name for gsi_name, hero in self.heroes.items()}
        item_id_to_name = {item['id']: item_key for item_key, item in self.items.items()}
        # ability_ids (not self.abilities) is the OpenDota resource that carries numeric ability ids.
        ability_id_to_name = {int(ability_id): name for ability_id, name in self.ability_ids.items()}

        hero_win_rates = {}
        hero_counters = {}
        hero_builds = {}
        heroes = list(hero_id_to_name.items())
        for index, (hero_id, gsi_name) in enumerate(heroes, start=1):
            response = await self.fetch_stratz_json(STRATZ_HERO_QUERY, {'heroId': hero_id})
            hero_stats = response['data']['heroStats']

            # winGameVersion returns one row per patch, most recent first.
            version_rows = hero_stats['winGameVersion']
            if version_rows:
                version_row = version_rows[0]
                match_count = version_row['matchCount']
                hero_win_rates[gsi_name] = {
                    'game_version_id': version_row['gameVersionId'],
                    'match_count': match_count,
                    'win_rate': version_row['winCount'] / match_count if match_count else None
                }

            # advantage[0].vs is the full counter list sorted by synergy; take:150 covers every hero.
            counters = {}
            matchup_rows = hero_stats['heroVsHeroMatchup']['advantage']
            if matchup_rows:
                for opponent in matchup_rows[0]['vs']:
                    opponent_name = hero_id_to_name.get(opponent['heroId2'])
                    if opponent_name:
                        counters[opponent_name] = {
                            'win_rate': opponent['winRateHeroId1'],
                            'synergy': opponent['synergy'],
                            'match_count': opponent['matchCount']
                        }
            hero_counters[gsi_name] = counters

            hero_builds[gsi_name] = {
                'starting_items': self.normalize_stratz_rows(
                    hero_stats['itemStartingPurchase'], 'itemId', item_id_to_name, 'item',
                    extra_fields={'was_given': 'wasGiven'}
                ),
                'core_items': self.normalize_stratz_rows(
                    hero_stats['itemFullPurchase'], 'itemId', item_id_to_name, 'item',
                    extra_fields={'time_seconds': 'time'}
                ),
                'ability_min_level': self.normalize_stratz_rows(
                    hero_stats['abilityMinLevel'], 'abilityId', ability_id_to_name, 'ability',
                    extra_fields={'level': 'level'}
                ),
                'ability_max_level': self.normalize_stratz_rows(
                    hero_stats['abilityMaxLevel'], 'abilityId', ability_id_to_name, 'ability',
                    extra_fields={'level': 'level'}
                ),
                'talents': self.normalize_stratz_rows(hero_stats['talent'], 'abilityId', ability_id_to_name, 'talent')
            }
            if index % 25 == 0 or index == len(heroes):
                logger.info(f'STRATZ hero data loading: {index}/{len(heroes)}')
        return hero_win_rates, hero_counters, hero_builds

    def normalize_stratz_rows(self, rows: list, id_field: str, id_map: dict, name_key: str, extra_fields: dict | None = None):
        """Return one representative row per STRATZ id, mapped to a GSI name and sorted by match count."""
        best_rows = {}
        for row in rows:
            name = id_map.get(row.get(id_field))
            if name is None:
                continue
            # Keep the most common row per id (highest match count) to stay compact.
            if name not in best_rows or row.get('matchCount', 0) > best_rows[name].get('matchCount', 0):
                best_rows[name] = row

        normalized = []
        for name, row in best_rows.items():
            match_count = row.get('matchCount') or 0
            wins_average = row.get('winsAverage')
            win_count = row.get('winCount')
            win_rate = wins_average if wins_average is not None else (
                win_count / match_count if match_count and win_count is not None else None
            )
            entry = {name_key: name, 'match_count': match_count, 'win_rate': win_rate}
            for target_key, source_key in (extra_fields or {}).items():
                entry[target_key] = row.get(source_key)
            normalized.append(entry)
        normalized.sort(key=lambda entry: entry['match_count'], reverse=True)
        return normalized

    def normalize_hero_mechanics(self, hero: dict):
        """Return compact hero mechanics for AI context."""
        abilities = [self.normalize_ability_or_item(ability) for ability in hero.get('abilities', [])]
        talents = [self.normalize_ability_or_item(talent) for talent in hero.get('talents', [])]
        return {
            'id': hero.get('id'),
            'name': hero.get('name'),
            'name_loc': hero.get('name_loc'),
            'facets': hero.get('facets', []),
            'primary_attr': hero.get('primary_attr'),
            'attack_capability': hero.get('attack_capability'),
            'role_levels': hero.get('role_levels'),
            'abilities': abilities,
            'talents': talents,
            'shard': [
                ability for ability in abilities
                if ability['ability_has_shard'] or ability['ability_is_granted_by_shard'] or ability['shard_loc']
            ],
            'scepter': [
                ability for ability in abilities
                if ability['ability_has_scepter'] or ability['ability_is_granted_by_scepter'] or ability['scepter_loc']
            ]
        }

    def normalize_ability_or_item(self, ability: dict):
        """Return compact ability or item mechanics for AI context."""
        return {
            'id': ability.get('id'),
            'name': ability.get('name'),
            'name_loc': ability.get('name_loc'),
            'desc_loc': ability.get('desc_loc'),
            'notes_loc': ability.get('notes_loc', []),
            'shard_loc': ability.get('shard_loc'),
            'scepter_loc': ability.get('scepter_loc'),
            'facets_loc': ability.get('facets_loc', []),
            'behavior': ability.get('behavior'),
            'damage': ability.get('damage'),
            'immunity': ability.get('immunity'),
            'dispellable': ability.get('dispellable'),
            'max_level': ability.get('max_level'),
            'cast_ranges': ability.get('cast_ranges', []),
            'cooldowns': ability.get('cooldowns', []),
            'durations': ability.get('durations', []),
            'damages': ability.get('damages', []),
            'mana_costs': ability.get('mana_costs', []),
            'item_cost': ability.get('item_cost'),
            'special_values': self.normalize_special_values(ability.get('special_values', [])),
            'ability_has_scepter': ability.get('ability_has_scepter', False),
            'ability_has_shard': ability.get('ability_has_shard', False),
            'ability_is_granted_by_scepter': ability.get('ability_is_granted_by_scepter', False),
            'ability_is_granted_by_shard': ability.get('ability_is_granted_by_shard', False),
            'ability_is_innate': ability.get('ability_is_innate', False)
        }

    def normalize_special_values(self, special_values: list):
        """Return compact special values with upgrade data."""
        normalized_values = []
        for special_value in special_values:
            normalized_values.append({
                'name': special_value.get('name'),
                'heading_loc': special_value.get('heading_loc'),
                'values_float': special_value.get('values_float', []),
                'values_shard': special_value.get('values_shard', []),
                'values_scepter': special_value.get('values_scepter', []),
                'facet_bonus': special_value.get('facet_bonus'),
                'required_facet': special_value.get('required_facet')
            })
        return normalized_values

    def set_admin_update_notifier(self, notifier):
        """Store admin update notification callback."""
        self.admin_update_notifier = notifier

    async def notify_admins(self, text: str):
        """Send Dota data update notification to admins."""
        if self.admin_update_notifier is not None:
            await self.admin_update_notifier(text)


dota_data_service = DotaDataService()
