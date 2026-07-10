from app.models.database import db


class ClientLinkRepository:
    async def save_token(self, user_id: int, token: str):
        """Save GSI token for Telegram user."""
        conn = await db.get_connection()
        # Upsert keeps one active GSI token per Telegram user.
        await conn.execute('''
            INSERT INTO client_links (user_id, gsi_token)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                gsi_token = excluded.gsi_token,
                updated_at = CURRENT_TIMESTAMP
        ''', (user_id, token))
        await conn.commit()

    async def get_user_id_by_token(self, token: str):
        """Return Telegram user id linked to GSI token."""
        row = await db.fetchone('''
            SELECT user_id
            FROM client_links
            WHERE gsi_token = ?
        ''', (token,))
        if row is None:
            return None
        return row['user_id']

    async def get_user_token(self, user_id: int):
        """Return GSI token linked to user."""
        return await db.fetchone('''
            SELECT gsi_token, created_at, updated_at
            FROM client_links
            WHERE user_id = ?
        ''', (user_id,))


client_link_repository = ClientLinkRepository()
