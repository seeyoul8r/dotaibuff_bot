import asyncio
import json
import urllib.request
from datetime import UTC, datetime


OPENDOTA_BASE_URL = 'https://api.opendota.com/api'
DOTA_DATA_UPDATE_INTERVAL = 60 * 60 * 24


class DotaDataService:
    def __init__(self):
        """Create empty Dota data holder."""
        self.updated_at = None
        self.is_ready = False
        self.hero_stats = []
        self.heroes = {}
        self.items = {}
        self.abilities = {}
        self.patches = []
        self.latest_patch = None
        self.patch_notes = {}

    async def start_daily_update(self):
        """Start daily Dota data update loop."""
        await self.update_data()
        while True:
            await asyncio.sleep(DOTA_DATA_UPDATE_INTERVAL)
            await self.update_data()

    async def update_data(self):
        """Update all collected Dota data."""
        hero_stats = await self.fetch_opendota_json('/heroStats')
        heroes = await self.fetch_opendota_json('/constants/heroes')
        items = await self.fetch_opendota_json('/constants/items')
        abilities = await self.fetch_opendota_json('/constants/abilities')
        patches = await self.fetch_opendota_json('/constants/patch')

        # Replace all runtime data together after successful OpenDota requests.
        self.hero_stats = hero_stats
        self.heroes = heroes
        self.items = items
        self.abilities = abilities
        self.patches = patches
        self.latest_patch = patches[-1] if patches else None
        self.patch_notes = {}
        self.updated_at = datetime.now(UTC).isoformat()
        self.is_ready = True
        print(f'Dota data updated: updated_at={self.updated_at}')

    def get_data(self):
        """Return current collected Dota data."""
        return {
            'updated_at': self.updated_at,
            'is_ready': self.is_ready,
            'hero_stats': self.hero_stats,
            'heroes': self.heroes,
            'items': self.items,
            'abilities': self.abilities,
            'patches': self.patches,
            'latest_patch': self.latest_patch,
            'patch_notes': self.patch_notes
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


dota_data_service = DotaDataService()
