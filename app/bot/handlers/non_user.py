from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from app.bot.bot_instances import notify_admins
from app.bot.filters.user import IsRegisteredUser, IsRegisteredUserCallback
from app.bot.keyboards.inline import kb_user
from app.bot.messages import mes_user
from app.repositories.user_repository import user_repository


non_user_router = Router()

# Keep every unregistered update inside onboarding before user handlers run.
non_user_router.message.filter(~IsRegisteredUser())
non_user_router.callback_query.filter(~IsRegisteredUserCallback())


@non_user_router.message(CommandStart())
async def start(message: Message):
    """Register a new user and show the welcome menu."""
    raw_lang = message.from_user.language_code or 'en'
    lang = 'ru' if raw_lang.startswith('ru') else 'en'
    # Persist registration before showing actions protected by the registered-user filter.
    await user_repository.save_user(
        message.from_user.id,
        message.from_user.first_name,
        message.from_user.username,
        lang
    )
    await message.answer(text=mes_user[lang].welcome, reply_markup=kb_user[lang].mainMenu)
    # Notify admins only in the new-user router, so repeated /start commands do not notify them.
    await notify_admins(
        f'New user registered.\n'
        f'ID: {message.from_user.id}\n'
        f'Name: {message.from_user.first_name}\n'
        f'Username: {message.from_user.username}',
        parse_mode=None
    )


@non_user_router.message()
async def user_not_registered(message: Message):
    """Ask an unregistered user to start the bot."""
    raw_lang = message.from_user.language_code or 'en'
    lang = 'ru' if raw_lang.startswith('ru') else 'en'
    # Explain the service before directing the user into registration.
    await message.answer(text=mes_user[lang].unregistered)


@non_user_router.callback_query()
async def user_not_registered_callback(callback: CallbackQuery):
    """Ask an unregistered callback sender to start the bot."""
    raw_lang = callback.from_user.language_code or 'en'
    lang = 'ru' if raw_lang.startswith('ru') else 'en'
    # Answer the stale button through chat, then stop Telegram's callback spinner.
    await callback.message.answer(text=mes_user[lang].unregistered)
    await callback.answer()
