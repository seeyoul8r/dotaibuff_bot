from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from app.bot.keyboards.inline import kb_user
from app.bot.messages import mes_user
from app.cache.redis_cache import redis_cache
from app.repositories.user_repository import user_repository
from app.services.client_link_service import client_link_service
from app.services.game_advisor_service import game_advisor_service


user_router = Router()
GET_GSI_CONFIG = 'get_gsi_config'
WHAT_IS_GSI_CONFIG = 'what_is_gsi_config'
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


@user_router.callback_query(lambda callback: callback.data == WHAT_IS_GSI_CONFIG)
async def explain_gsi_config(callback: CallbackQuery):
    """Explain GSI config setup."""
    lang = await user_repository.get_user_lang(callback.from_user.id)
    # Send localized GSI setup instructions without changing the menu.
    await callback.message.answer(text=mes_user[lang].gsi_config_info)
    await callback.answer()


@user_router.callback_query(lambda callback: callback.data == GET_AI_ADVICE)
async def send_ai_advice(callback: CallbackQuery):
    """Send structured AI game advice."""
    lang = await user_repository.get_user_lang(callback.from_user.id)
    match_id = await redis_cache.get_active_match(callback.from_user.id)
    match_state = None if match_id is None else await redis_cache.get_match_state(callback.from_user.id, match_id)
    if match_state is None:
        # Do not start cooldown or paid AI request until accumulated match data exists.
        await callback.answer()
        await callback.message.answer(text=mes_user[lang].snapshot_not_received)
        return

    remaining_time = game_advisor_service.is_on_cooldown(callback.from_user.id)
    if remaining_time > 0:
        await callback.answer(text=mes_user[lang].advice_on_cooldown(remaining_time), show_alert=True)
        return

    # Set cooldown before the paid request to block repeated button presses.
    game_advisor_service.set_cooldown(callback.from_user.id)
    await callback.answer()
    advice = await game_advisor_service.request_advice(callback.from_user.id, lang)
    await callback.message.answer(
        text=f'{mes_user[lang].macro_advice_title}\n\n{advice.macro_gaming}',
        parse_mode=None
    )
    await callback.message.answer(
        text=f'{mes_user[lang].build_advice_title}\n\n{advice.build}',
        parse_mode=None
    )
    await callback.message.answer(
        text=f'{mes_user[lang].micro_advice_title}\n\n{advice.micro_gaming}',
        parse_mode=None
    )


@user_router.callback_query(lambda callback: callback.data == CHANGE_LANGUAGE)
async def change_language(callback: CallbackQuery):
    """Switch current user language."""
    current_lang = await user_repository.get_user_lang(callback.from_user.id)
    lang = 'en' if current_lang == 'ru' else 'ru'
    await user_repository.set_user_lang(callback.from_user.id, lang)
    # Redraw menu with the newly selected language.
    await callback.message.edit_text(text=mes_user[lang].language_changed, reply_markup=kb_user[lang].mainMenu)
    await callback.answer()
