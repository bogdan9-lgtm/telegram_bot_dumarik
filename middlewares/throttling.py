import logging
import time

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message

logger = logging.getLogger(__name__)

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 1.0):
        # К-сть секунд між запитами
        self.rate_limit: float = rate_limit
        self.last_call: dict[int, float] = {}
        self.busy: set[int] = set()


    async def __call__(self, handler, event: TelegramObject, data: dict):
        user = data.get("event_from_user")

        if user is None:
            return await handler(event, data)

        if user.id in self.busy:
            logger.info("Тротлінг: користувач %s не дочекався відповіді", user.id)
            await self.warn(event, "Зачекай, я ще думаю над попереднім ⏳")
            return None

        now = time.monotonic()

        if now - self.last_call.get(user.id, 0) < self.rate_limit:
            logger.info("Тротлінг: користувач %s пише надто швидко", user.id)
            await self.warn(event, "Не так швидко 🙂")
            return None

        self.busy.add(user.id)

        try:
            return await handler(event, data)
        finally:
            self.busy.discard(user.id)
            self.last_call[user.id] = time.monotonic()


    async def warn(self, event: TelegramObject, text: str):
        if isinstance(event, CallbackQuery):
            await event.answer(text)
        elif isinstance(event, Message):
            await event.answer(text)