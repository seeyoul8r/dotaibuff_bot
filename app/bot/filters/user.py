from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message

from app.repositories.user_repository import user_repository


class IsRegisteredUser(Filter):
    async def __call__(self, message: Message) -> bool:
        """Allow messages only from registered users."""
        # Read registration from SQLite so filtering uses the current persisted state.
        return await user_repository.get_user(message.from_user.id) is not None


class IsRegisteredUserCallback(Filter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        """Allow callbacks only from registered users."""
        # Read registration from SQLite so filtering uses the current persisted state.
        return await user_repository.get_user(callback.from_user.id) is not None
