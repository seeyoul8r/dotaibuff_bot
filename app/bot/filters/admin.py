from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message


class IsAdmin(Filter):
    def __init__(self, admin_ids: list[int]):
        """Store allowed admin ids."""
        self.admin_ids = admin_ids

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        """Allow updates only from configured admins."""
        # Aiogram passes either messages or callbacks, both expose from_user.
        return event.from_user.id in self.admin_ids
