import asyncio
import logging

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from app.bot.bot_instances import admin_bot, bot
from app.bot.handlers import admin_router, user_router
from app.models.database import db


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def start_bot():
    """Start main Telegram bot polling."""
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(user_router)
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Start bot')
    ]
    await bot.set_my_commands(main_menu_commands)
    # Drop old webhook updates before polling this bot.
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, skip_updates=True)


async def start_admin_bot():
    """Start admin Telegram bot polling."""
    admin_dp = Dispatcher(storage=MemoryStorage())
    admin_dp.include_router(admin_router)
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Start admin bot')
    ]
    await admin_bot.set_my_commands(main_menu_commands)
    # Drop old webhook updates before polling this bot.
    await admin_bot.delete_webhook(drop_pending_updates=True)
    await admin_dp.start_polling(admin_bot, skip_updates=True)


async def start_app():
    """Initialize database and start Telegram bots."""
    # Create SQLite structure before accepting Telegram updates.
    await db.create_tables()
    try:
        await asyncio.gather(start_bot(), start_admin_bot())
    finally:
        # Close SQLite connection when polling is stopped.
        await db.close()


def main():
    """Run Telegram bot application."""
    asyncio.run(start_app())


if __name__ == '__main__':
    main()
