from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import BufferedInputFile, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.services.client_link_service import client_link_service
from app.services.game_advisor_service import game_advisor_service


user_router = Router()
GET_GSI_CONFIG = 'get_gsi_config'
GET_AI_ADVICE = 'get_ai_advice'


@user_router.message(CommandStart())
async def start(message: Message):
    """Answer main bot start command."""
    # Show the first user action for linking Dota 2 GSI client.
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Получить GSI config', callback_data=GET_GSI_CONFIG)],
        [InlineKeyboardButton(text='Получить рекомендацию ИИ', callback_data=GET_AI_ADVICE)]
    ])
    await message.answer(text='DotAIBuffBot started.', reply_markup=keyboard)


@user_router.callback_query(lambda callback: callback.data == GET_GSI_CONFIG)
async def send_gsi_config(callback: CallbackQuery):
    """Send personal Dota 2 GSI config file."""
    config_text = await client_link_service.build_gsi_config(callback.from_user.id)
    config_file = BufferedInputFile(
        file=config_text.encode('utf-8'),
        filename='gamestate_integration_dot_ai_buff_bot.cfg'
    )
    # Send config as a file so user can place it into the Dota 2 GSI folder.
    await callback.message.answer_document(
        document=config_file,
        caption='Положи файл в папку Dota 2 gamestate_integration.'
    )
    await callback.answer()


@user_router.callback_query(lambda callback: callback.data == GET_AI_ADVICE)
async def send_ai_advice(callback: CallbackQuery):
    """Send current snapshot summary as AI advice preview."""
    advice = await game_advisor_service.request_advice(callback.from_user.id)
    # Send the latest parsed snapshot summary instead of real AI response for now.
    await callback.message.answer(text=advice)
    await callback.answer()
