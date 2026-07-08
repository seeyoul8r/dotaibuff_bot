from aiogram import Bot
from aiogram.client.bot import DefaultBotProperties

from app.core.config import Config, load_admin_config, load_config


config: Config = load_config()
BOT_TOKEN: str = config.tg_bot.token

admin_config: Config = load_admin_config()
ADMIN_BOT_TOKEN: str = admin_config.tg_bot.token

# Create bot instances once and reuse them in polling.
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML', protect_content=False))

admin_bot = Bot(token=ADMIN_BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML', protect_content=False))
