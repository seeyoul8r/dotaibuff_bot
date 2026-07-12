from pathlib import Path

import aiosqlite


DATA_DIR = Path('data')
DB_PATH = DATA_DIR / 'dot_ai_buff_bot.db'


class Database:
    def __init__(self, db_path: str):
        """Store database path and empty connection."""
        self.db_path = db_path
        self._connection = None

    async def get_connection(self):
        """Return current SQLite connection or create it."""
        # Create runtime data folder right before the first SQLite connection.
        DATA_DIR.mkdir(exist_ok=True)
        if self._connection is None:
            self._connection = await aiosqlite.connect(self.db_path)
            self._connection.row_factory = aiosqlite.Row
            await self._connection.execute('PRAGMA journal_mode=WAL;')
            await self._connection.execute('PRAGMA foreign_keys=ON;')
        return self._connection

    async def execute(self, sql: str, params: tuple = ()):
        """Execute SQL through the shared connection."""
        conn = await self.get_connection()
        return await conn.execute(sql, params)

    async def fetchone(self, sql: str, parameters: tuple = ()):
        """Fetch one row from SQLite."""
        conn = await self.get_connection()
        async with conn.execute(sql, parameters) as cursor:
            return await cursor.fetchone()

    async def fetchall(self, sql: str, parameters: tuple = ()):
        """Fetch all rows from SQLite."""
        conn = await self.get_connection()
        async with conn.execute(sql, parameters) as cursor:
            return await cursor.fetchall()

    async def close(self):
        """Close current SQLite connection."""
        if self._connection is not None:
            await self._connection.close()
            self._connection = None

    async def create_tables(self):
        """Create base database tables."""
        conn = await self.get_connection()
        # Store Telegram users in one small base table for future bot features.
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                username TEXT,
                is_admin INTEGER DEFAULT 0,
                lang TEXT DEFAULT 'ru',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Link generated GSI config tokens to Telegram users.
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS client_links (
                user_id INTEGER PRIMARY KEY,
                gsi_token TEXT UNIQUE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Store full AI advice request lifecycle for later analysis.
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS ai_requests (
                request_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                match_id INTEGER,
                request_started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                request TEXT NOT NULL,
                response_finished_at DATETIME,
                response TEXT,
                model TEXT NOT NULL,
                system_instruction TEXT NOT NULL,
                response_mime_type TEXT NOT NULL,
                response_schema TEXT NOT NULL,
                thinking_level TEXT NOT NULL,
                status TEXT NOT NULL,
                error TEXT
            )
        ''')
        await conn.commit()


db = Database(str(DB_PATH))
