import logging
import time

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message

import keyboards.reply as reply_kb

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

        state = data.get("state")
        if isinstance(event, Message) and state is not None:
            current_state = await state.get_state()
            text = (event.text or "").strip()
            command = text.split(maxsplit=1)[0].split("@", maxsplit=1)[0].lower() if text.startswith("/") else ""
            starts_another_function = (
                text in reply_kb.MENU_BUTTONS
                or (command.startswith("/") and command not in {"/start", "/help"})
            )

            if current_state is not None and starts_another_function:
                await self.warn(
                    event,
                    "Спершу заверши поточну функцію або повернись у меню командою /start.",
                )
                return None

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