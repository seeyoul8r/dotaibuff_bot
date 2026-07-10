from app.models.database import db


class UserRepository:
    async def save_user(self, user_id: int, first_name: str | None, username: str | None, lang: str):
        """Save Telegram user profile."""
        conn = await db.get_connection()
        # Preserve existing language while updating Telegram profile fields.
        await conn.execute('''
            INSERT INTO users (user_id, first_name, username, lang)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                first_name = excluded.first_name,
                username = excluded.username
        ''', (user_id, first_name, username, lang))
        await conn.commit()

    async def get_user_lang(self, user_id: int):
        """Return saved user language."""
        row = await db.fetchone('''
            SELECT lang
            FROM users
            WHERE user_id = ?
        ''', (user_id,))
        return row['lang']

    async def set_user_lang(self, user_id: int, lang: str):
        """Save selected user language."""
        conn = await db.get_connection()
        await conn.execute('''
            UPDATE users
            SET lang = ?
            WHERE user_id = ?
        ''', (lang, user_id))
        await conn.commit()

    async def get_user(self, user_id: int):
        """Return saved user profile."""
        return await db.fetchone('''
            SELECT user_id, first_name, username, is_admin, lang, created_at
            FROM users
            WHERE user_id = ?
        ''', (user_id,))

    async def get_users(self):
        """Return saved user profiles."""
        return await db.fetchall('''
            SELECT user_id, first_name, username, is_admin, lang, created_at
            FROM users
            ORDER BY created_at DESC
        ''')


user_repository = UserRepository()
