from pathlib import Path

from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.bot.bot_instances import admin_config, bot
from app.bot.filters.admin import IsAdmin
from app.bot.keyboards.inline.admin import adminCancelKb, adminMainKb
from app.models.database import db
from app.repositories.client_link_repository import client_link_repository
from app.repositories.user_repository import user_repository
from app.services.dota_data_service import dota_data_service
from app.services.game_advisor_service import game_advisor_service


admin_router = Router()
UPDATE_DOTA_DATA = 'update_dota_data'
ERROR_LOG_PATH = Path('error_log.txt')
ENV_PATH = Path('.env')

admin_router.message.filter(IsAdmin(admin_config.tg_bot.admin_ids))
admin_router.callback_query.filter(IsAdmin(admin_config.tg_bot.admin_ids))


class AdminStates(StatesGroup):
    manage_user = State()
    send_all = State()
    advice_cooldown = State()


@admin_router.message(CommandStart())
async def admin_start(message: Message):
    """Answer admin bot start command."""
    # Show available admin maintenance actions.
    await message.answer(text='DotAIBuffBot admin started.', reply_markup=adminMainKb)


@admin_router.callback_query(lambda callback: callback.data == 'cancel_input')
async def cancel_input(callback: CallbackQuery, state: FSMContext):
    """Cancel current admin input."""
    await state.clear()
    await callback.message.answer(text='Input cancelled.', reply_markup=adminMainKb)
    await callback.answer()


@admin_router.callback_query(lambda callback: callback.data == UPDATE_DOTA_DATA)
async def update_dota_data(callback: CallbackQuery):
    """Run Dota data update manually."""
    await callback.answer()
    # Reuse the regular update flow so admins receive start, finish, or failure notifications.
    await dota_data_service.update_data()


@admin_router.callback_query(lambda callback: callback.data == 'admin_update_db')
async def update_db(callback: CallbackQuery):
    """Create missing database tables."""
    await db.create_tables()
    await callback.message.answer(text='DB update finished.', reply_markup=adminMainKb)
    await callback.answer()


@admin_router.callback_query(lambda callback: callback.data == 'admin_users_list')
async def users_list(callback: CallbackQuery):
    """Send saved users list."""
    users = await user_repository.get_users()
    if not users:
        await callback.message.answer(text='No users found.', reply_markup=adminMainKb)
        await callback.answer()
        return

    lines = ['Users:']
    for user in users:
        username = f'@{user["username"]}' if user['username'] else '-'
        lines.append(f'{user["user_id"]} | {username} | {user["first_name"]} | {user["lang"]}')
    await callback.message.answer(text='\n'.join(lines), reply_markup=adminMainKb, parse_mode=None)
    await callback.answer()


@admin_router.callback_query(lambda callback: callback.data == 'admin_manage_user')
async def manage_user_input(callback: CallbackQuery, state: FSMContext):
    """Ask admin for user id."""
    await state.clear()
    await callback.message.answer(text='Input user id you want to manage:', reply_markup=adminCancelKb)
    await state.set_state(AdminStates.manage_user)
    await callback.answer()


@admin_router.message(StateFilter(AdminStates.manage_user))
async def manage_user_value(message: Message, state: FSMContext):
    """Show selected user info."""
    try:
        user_id = int(message.text)
        user = await user_repository.get_user(user_id)
        if user is None:
            raise ValueError('User not found')
        client_link = await client_link_repository.get_user_token(user_id)
        token = '-' if client_link is None else f'{client_link["gsi_token"][:8]}...'
        text = (
            f'User ID: {user["user_id"]}\n'
            f'First name: {user["first_name"]}\n'
            f'Username: {user["username"]}\n'
            f'Language: {user["lang"]}\n'
            f'Admin: {user["is_admin"]}\n'
            f'Created: {user["created_at"]}\n'
            f'GSI token: {token}'
        )
        await message.answer(text=text, reply_markup=adminMainKb, parse_mode=None)
        await state.clear()
    except Exception as error:
        await message.answer(text=f'Wrong input. {error}', reply_markup=adminCancelKb)


@admin_router.callback_query(lambda callback: callback.data == 'admin_send_all')
async def send_all_input(callback: CallbackQuery, state: FSMContext):
    """Ask admin for broadcast text."""
    await state.clear()
    await callback.message.answer(text='Input message you want to send to users:', reply_markup=adminCancelKb)
    await state.set_state(AdminStates.send_all)
    await callback.answer()


@admin_router.message(StateFilter(AdminStates.send_all))
async def send_all_value(message: Message, state: FSMContext):
    """Send admin message to all users."""
    users = await user_repository.get_users()
    sent_count = 0
    failed_count = 0
    for user in users:
        try:
            await bot.send_message(user['user_id'], message.text, parse_mode=None)
            sent_count += 1
        except Exception:
            # Keep broadcast going even when one user blocked the bot.
            failed_count += 1
    await message.answer(text=f'Messages sent. Sent: {sent_count}, failed: {failed_count}.', reply_markup=adminMainKb)
    await state.clear()


@admin_router.callback_query(lambda callback: callback.data == 'admin_set_advice_cooldown')
async def advice_cooldown_input(callback: CallbackQuery, state: FSMContext):
    """Ask admin for new advice cooldown."""
    await state.clear()
    await callback.message.answer(text='Input AI advice cooldown in seconds:', reply_markup=adminCancelKb)
    await state.set_state(AdminStates.advice_cooldown)
    await callback.answer()


@admin_router.message(StateFilter(AdminStates.advice_cooldown))
async def advice_cooldown_value(message: Message, state: FSMContext):
    """Update advice cooldown and reload config."""
    try:
        cooldown = int(message.text)
        if cooldown < 0:
            raise ValueError('Cooldown must be non-negative')
        update_env_value('AI_ADVICE_COOLDOWN', str(cooldown))
        game_advisor_service.reload_config()
        await message.answer(text=f'AI advice cooldown updated: {cooldown} sec.', reply_markup=adminMainKb)
        await state.clear()
    except Exception as error:
        await message.answer(text=f'Wrong input. {error}', reply_markup=adminCancelKb)


@admin_router.callback_query(lambda callback: callback.data == 'admin_show_errors')
async def show_errors(callback: CallbackQuery):
    """Show current error log."""
    if not ERROR_LOG_PATH.exists() or ERROR_LOG_PATH.stat().st_size == 0:
        await callback.message.answer(text='Error log is empty.', reply_markup=adminMainKb)
        await callback.answer()
        return
    text = ERROR_LOG_PATH.read_text(encoding='utf-8')[-3500:]
    await callback.message.answer(text=text, reply_markup=adminMainKb, parse_mode=None)
    await callback.answer()


@admin_router.callback_query(lambda callback: callback.data == 'admin_clean_errors')
async def clean_errors(callback: CallbackQuery):
    """Clean current error log."""
    ERROR_LOG_PATH.write_text('', encoding='utf-8')
    await callback.message.answer(text='Error log cleaned.', reply_markup=adminMainKb)
    await callback.answer()


def update_env_value(key: str, value: str):
    """Update one .env key."""
    lines = ENV_PATH.read_text(encoding='utf-8').splitlines() if ENV_PATH.exists() else []
    updated_lines = []
    updated = False
    for line in lines:
        if line.startswith(f'{key}='):
            updated_lines.append(f'{key}={value}')
            updated = True
        else:
            updated_lines.append(line)
    if not updated:
        updated_lines.append(f'{key}={value}')
    ENV_PATH.write_text('\n'.join(updated_lines) + '\n', encoding='utf-8')
