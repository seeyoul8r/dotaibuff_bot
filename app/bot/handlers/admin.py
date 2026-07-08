from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.bot_instances import admin_config
from app.bot.filters.admin import IsAdmin


admin_router = Router()

admin_router.message.filter(IsAdmin(admin_config.tg_bot.admin_ids))
admin_router.callback_query.filter(IsAdmin(admin_config.tg_bot.admin_ids))


@admin_router.message(CommandStart())
async def admin_start(message: Message):
    """Answer admin bot start command."""
    # Keep the first admin response minimal until admin commands exist.
    await message.answer(text='DotAIBuffBot admin started.')
