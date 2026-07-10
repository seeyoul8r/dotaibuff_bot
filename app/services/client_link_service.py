import secrets

from app.core.config import ServerConfig, load_server_config
from app.repositories.client_link_repository import client_link_repository


class ClientLinkService:
    def __init__(self):
        """Store server networking configuration."""
        self.server_config: ServerConfig = load_server_config()

    async def create_user_token(self, user_id: int):
        """Create and save GSI token for user."""
        # Generate a unique token used by Dota 2 GSI auth payload.
        token = secrets.token_urlsafe(32)
        await client_link_repository.save_token(user_id, token)
        return token

    async def get_user_by_token(self, token: str):
        """Return user id linked to GSI token."""
        return await client_link_repository.get_user_id_by_token(token)

    async def build_gsi_config(self, user_id: int):
        """Build Dota 2 GSI config for user."""
        token = await self.create_user_token(user_id)
        # Config contains the token that links incoming snapshots to Telegram user.
        return f'''"DotAIBuffBot"
{{
    "uri" "{self.server_config.gsi_public_url}"
    "timeout" "5.0"
    "buffer" "0.1"
    "throttle" "0.1"
    "heartbeat" "30.0"
    "auth"
    {{
        "token" "{token}"
    }}
    "data"
    {{
        "provider" "1"
        "map" "1"
        "player" "1"
        "hero" "1"
        "abilities" "1"
        "items" "1"
        "buildings" "1"
        "minimap" "1"
    }}
}}'''


client_link_service = ClientLinkService()
