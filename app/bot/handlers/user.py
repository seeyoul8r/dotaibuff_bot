from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message


user_router = Router()


@user_router.message(CommandStart())
async def start(message: Message):
    """Answer main bot start command."""
    # Keep the first user response minimal until the real menu exists.
    await message.answer(text='DotAIBuffBot started.')
