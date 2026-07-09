from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import BufferedInputFile, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.services.client_link_service import client_link_service


user_router = Router()
GET_GSI_CONFIG = 'get_gsi_config'


@user_router.message(CommandStart())
async def start(message: Message):
    """Answer main bot start command."""
    # Show the first user action for linking Dota 2 GSI client.
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Получить GSI config', callback_data=GET_GSI_CONFIG)]
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
