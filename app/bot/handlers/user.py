from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from app.bot.keyboards.inline import kb_user
from app.bot.messages import mes_user
from app.repositories.user_repository import user_repository
from app.services.client_link_service import client_link_service
from app.services.game_advisor_service import game_advisor_service


user_router = Router()
GET_GSI_CONFIG = 'get_gsi_config'
GET_AI_ADVICE = 'get_ai_advice'
CHANGE_LANGUAGE = 'change_language'


@user_router.message(CommandStart())
async def start(message: Message):
    """Answer main bot start command."""
    raw_lang = message.from_user.language_code or 'en'
    lang = 'ru' if raw_lang.startswith('ru') else 'en'
    await user_repository.save_user(message.from_user.id, message.from_user.first_name, message.from_user.username, lang)
    # Show localized user actions for GSI config and advice preview.
    await message.answer(text=mes_user[lang].start_text, reply_markup=kb_user[lang].mainMenu)


@user_router.callback_query(lambda callback: callback.data == GET_GSI_CONFIG)
async def send_gsi_config(callback: CallbackQuery):
    """Send personal Dota 2 GSI config file."""
    lang = await user_repository.get_user_lang(callback.from_user.id)
    config_text = await client_link_service.build_gsi_config(callback.from_user.id)
    config_file = BufferedInputFile(
        file=config_text.encode('utf-8'),
        filename='gamestate_integration_dot_ai_buff_bot.cfg'
    )
    # Send config as a file so user can place it into the Dota 2 GSI folder.
    await callback.message.answer_document(
        document=config_file,
        caption=mes_user[lang].gsi_config_caption
    )
    await callback.answer()


@user_router.callback_query(lambda callback: callback.data == GET_AI_ADVICE)
async def send_ai_advice(callback: CallbackQuery):
    """Send current snapshot summary as AI advice preview."""
    lang = await user_repository.get_user_lang(callback.from_user.id)
    advice = await game_advisor_service.request_advice(callback.from_user.id, lang)
    # Send the latest parsed snapshot summary instead of real AI response for now.
    await callback.message.answer(text=advice)
    await callback.answer()


@user_router.callback_query(lambda callback: callback.data == CHANGE_LANGUAGE)
async def change_language(callback: CallbackQuery):
    """Switch current user language."""
    current_lang = await user_repository.get_user_lang(callback.from_user.id)
    lang = 'en' if current_lang == 'ru' else 'ru'
    await user_repository.set_user_lang(callback.from_user.id, lang)
    # Redraw menu with the newly selected language.
    await callback.message.edit_text(text=mes_user[lang].language_changed, reply_markup=kb_user[lang].mainMenu)
    await callback.answer()
