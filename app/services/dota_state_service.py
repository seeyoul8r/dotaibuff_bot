class DotaStateService:
    def __init__(self):
        """Create empty Dota state holder."""
        self.patch_notes = None
        self.dotabuff_stats = None

    async def get_patch_notes(self):
        """Return current patch notes data."""
        return self.patch_notes

    async def get_dotabuff_stats(self):
        """Return current Dotabuff stats."""
        return self.dotabuff_stats

    async def get_current_state(self):
        """Return combined current Dota state."""
        # Keep patch notes and stats together for AI prompt building.
        return {
            'patch_notes': await self.get_patch_notes(),
            'dotabuff_stats': await self.get_dotabuff_stats()
        }


dota_state_service = DotaStateService()
