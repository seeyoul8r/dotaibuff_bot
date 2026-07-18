import asyncio
import logging

from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from app.bot.keyboards.inline import kb_user
from app.bot.messages import mes_user
from app.cache.redis_cache import redis_cache
from app.repositories.user_repository import user_repository
from app.services.client_link_service import client_link_service
from app.services.dota_data_service import dota_data_service
from app.services.game_advisor_service import game_advisor_service
from app.services.map_location_service import UNKNOWN_LOCATION_SLUG


logger = logging.getLogger(__name__)
user_router = Router()
GET_GSI_CONFIG = 'get_gsi_config'
WHAT_IS_GSI_CONFIG = 'what_is_gsi_config'
OPEN_GSI_MENU = 'open_gsi_menu'
BACK_TO_MAIN_MENU = 'back_to_main_menu'
GET_AI_ADVICE = 'get_ai_advice'
WHERE_ARE_ENEMIES = 'where_are_enemies'
CHANGE_LANGUAGE = 'change_language'
DRAFT_UPDATE_INTERVAL = 20
MAP_LOCATION_WORDS = {
    'big': 'Big',
    'bot': 'Bot',
    'bridge': 'Bridge',
    'dire': 'Dire',
    'forest': 'Forest',
    'fountain': 'Fountain',
    'graveyard': 'Graveyard',
    'hardlane': 'Hard Lane',
    'highground': 'High Ground',
    'jungle': 'Jungle',
    'lotus': 'Lotus',
    'mid': 'Mid',
    'midlane': 'Mid Lane',
    'mines': 'Mines',
    'offlane': 'Offlane',
    'pit': 'Pit',
    'pool': 'Pool',
    'radiant': 'Radiant',
    'river': 'River',
    'roshan': 'Roshan',
    'safelane': 'Safe Lane',
    'secret': 'Secret',
    'shop': 'Shop',
    'small': 'Small',
    'statue': 'Statue',
    'tormentor': 'Tormentor',
    'top': 'Top',
    'triangle': 'Triangle',
    'throne': 'Throne',
    'twin': 'Twin',
    'gate': 'Gate',
    't1': 'T1',
    't2': 'T2',
    't3': 'T3',
    'well': 'Well',
    'wisdom': 'Wisdom',
    'rune': 'Rune'
}


async def keep_advice_draft(bot: Bot, chat_id: int, draft_id: int):
    """Keep native Telegram thinking draft visible."""
    while True:
        # Empty draft text shows Telegram's native animated Thinking placeholder.
        await bot.send_message_draft(chat_id=chat_id, draft_id=draft_id, text='')
        await asyncio.sleep(DRAFT_UPDATE_INTERVAL)


@user_router.message(CommandStart())
async def start(message: Message):
    """Answer main bot start command."""
    lang = await user_repository.get_user_lang(message.from_user.id)
    await user_repository.save_user(message.from_user.id, message.from_user.first_name, message.from_user.username, lang)
    # Show localized user actions for GSI config and advice preview.
    await message.answer(text=mes_user[lang].start_text, reply_markup=kb_user[lang].mainMenu)


@user_router.callback_query(F.data.in_({OPEN_GSI_MENU, BACK_TO_MAIN_MENU}))
async def switch_user_menu(callback: CallbackQuery):
    """Switch user inline menu."""
    lang = await user_repository.get_user_lang(callback.from_user.id)
    reply_markup = kb_user[lang].gsiMenu if callback.data == OPEN_GSI_MENU else kb_user[lang].mainMenu
    # Redraw only buttons so menu navigation does not regenerate the client link token.
    await callback.message.edit_reply_markup(reply_markup=reply_markup)
    await callback.answer()


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
    draft_task = asyncio.create_task(
        keep_advice_draft(callback.bot, callback.from_user.id, callback.message.message_id)
    )
    try:
        advice = await game_advisor_service.request_advice(callback.from_user.id, lang)
    except Exception as error:
        logger.exception(f'Gemini advice request failed: user_id={callback.from_user.id}, error={error}')
        advice = None
    finally:
        # Stop the ephemeral draft before sending persistent result messages.
        draft_task.cancel()
        await asyncio.gather(draft_task, return_exceptions=True)

    if advice is None:
        await callback.message.answer(text=mes_user[lang].advice_request_failed)
        return

    advice_time = mes_user[lang].advice_actual_at(match_state.get('clock_time'))
    # Send one persistent result message so Telegram keeps the whole answer visible after the draft.
    await callback.message.answer(
        text=(
            f'{advice_time}\n\n'
            f'{mes_user[lang].macro_advice_title}\n\n{advice.macro_gaming}\n\n'
            f'{mes_user[lang].build_advice_title}\n\n{advice.build}\n\n'
            f'{mes_user[lang].micro_advice_title}\n\n{advice.micro_gaming}\n\n'
            f'{mes_user[lang].next_advice_available(int(game_advisor_service.config.advice_cooldown))}'
        ),
        parse_mode=None,
        reply_markup=kb_user[lang].afterAdviceMenu
    )


@user_router.callback_query(lambda callback: callback.data == WHERE_ARE_ENEMIES)
async def send_enemy_map_info(callback: CallbackQuery):
    """Send current enemy map info."""
    lang = await user_repository.get_user_lang(callback.from_user.id)
    match_id = await redis_cache.get_active_match(callback.from_user.id)
    match_state = None if match_id is None else await redis_cache.get_match_state(callback.from_user.id, match_id)
    if match_state is None:
        # Do not show enemy info until accumulated match data exists.
        await callback.answer()
        await callback.message.answer(text=mes_user[lang].snapshot_not_received)
        return

    match_time = mes_user[lang].advice_actual_at(match_state.get('clock_time'))
    enemy_map_info = format_enemy_map_info(match_state, lang)
    # Send enemy positions separately from paid AI advice.
    await callback.message.answer(
        text=(
            f'{match_time}\n\n'
            f'{enemy_map_info}'
        ),
        parse_mode=None,
        reply_markup=kb_user[lang].afterAdviceMenu
    )
    await callback.answer()


def format_enemy_map_info(match_state: dict, lang: str):
    """Return enemy last seen table."""
    player_team_name = match_state.get('player', {}).get('team_name')
    opponent_team_name = {'radiant': 'dire', 'dire': 'radiant'}.get(player_team_name)
    if opponent_team_name is None:
        return ''

    current_game_time = match_state.get('clock_time')
    dota_data = dota_data_service.get_data()
    lines = []
    for hero_name, hero_state in match_state[opponent_team_name]['heroes'].items():
        last_seen_game_time = hero_state.get('last_seen_game_time')
        seen_seconds_ago = None
        if isinstance(current_game_time, (int, float)) and isinstance(last_seen_game_time, (int, float)):
            # Use game clock delta to keep table timing aligned with match time.
            seen_seconds_ago = max(0, int(current_game_time - last_seen_game_time))
        if seen_seconds_ago is None and not hero_state.get('visible', False):
            seen_time = mes_user[lang].enemy_no_seen_time
            location_title = mes_user[lang].enemy_not_seen_yet
        else:
            seen_time = mes_user[lang].enemy_seen_time(hero_state.get('visible', False), seen_seconds_ago)
            location_slug = hero_state.get('last_seen_location_slug', UNKNOWN_LOCATION_SLUG)
            # Keep detected area names English and generated from the stored slug.
            location_title = mes_user[lang].enemy_unknown_area if location_slug == UNKNOWN_LOCATION_SLUG else format_map_location_title(location_slug)
        hero_title = dota_data['heroes'][hero_name]['definition']['localized_name']
        lines.append(f'{hero_title} | {location_title} | {seen_time}')

    if not lines:
        return ''

    # Plain text table is used because outgoing advice disables Telegram parse mode.
    return f'{mes_user[lang].enemy_map_info_title}\n\n{mes_user[lang].enemy_map_info_header}\n' + '\n'.join(lines) + '\n\n'


def format_map_location_title(location_slug: str):
    """Return English readable map location title."""
    # Map internal slug tokens to readable English words used in both languages.
    return ' '.join(MAP_LOCATION_WORDS[word] for word in location_slug.split('_'))


@user_router.callback_query(lambda callback: callback.data == CHANGE_LANGUAGE)
async def change_language(callback: CallbackQuery):
    """Switch current user language."""
    current_lang = await user_repository.get_user_lang(callback.from_user.id)
    lang = 'en' if current_lang == 'ru' else 'ru'
    await user_repository.set_user_lang(callback.from_user.id, lang)
    # Redraw menu with the newly selected language.
    await callback.message.edit_text(text=mes_user[lang].language_changed, reply_markup=kb_user[lang].mainMenu)
    await callback.answer()
