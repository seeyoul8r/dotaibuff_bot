from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.bot.bot_instances import admin_config
from app.bot.filters.admin import IsAdmin
from app.services.dota_data_service import dota_data_service


admin_router = Router()
UPDATE_DOTA_DATA = 'update_dota_data'
admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Update Dota data', callback_data=UPDATE_DOTA_DATA)]
])

admin_router.message.filter(IsAdmin(admin_config.tg_bot.admin_ids))
admin_router.callback_query.filter(IsAdmin(admin_config.tg_bot.admin_ids))


@admin_router.message(CommandStart())
async def admin_start(message: Message):
    """Answer admin bot start command."""
    # Show available admin maintenance actions.
    await message.answer(text='DotAIBuffBot admin started.', reply_markup=admin_menu)


@admin_router.callback_query(lambda callback: callback.data == UPDATE_DOTA_DATA)
async def update_dota_data(callback: CallbackQuery):
    """Run Dota data update manually."""
    await callback.answer()
    # Reuse the regular update flow so admins receive start, finish, or failure notifications.
    await dota_data_service.update_data()
