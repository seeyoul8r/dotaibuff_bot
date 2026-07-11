import logging

from aiogram import Bot
from aiogram.client.bot import DefaultBotProperties

from app.core.config import Config, load_admin_config, load_config


logger = logging.getLogger(__name__)

config: Config = load_config()
BOT_TOKEN: str = config.tg_bot.token

admin_config: Config = load_admin_config()
ADMIN_BOT_TOKEN: str = admin_config.tg_bot.token

# Create bot instances once and reuse them in polling.
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML', protect_content=False))

admin_bot = Bot(token=ADMIN_BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML', protect_content=False))


async def notify_admins(text: str, **kwargs):
    """Send a notification to every configured admin."""
    for admin_id in admin_config.tg_bot.admin_ids:
        try:
            # Keep other admin notifications running if one chat is unavailable.
            await admin_bot.send_message(admin_id, text=text, **kwargs)
        except Exception as error:
            logger.error(f'Admin notification failed: admin_id={admin_id}, error={error}')
