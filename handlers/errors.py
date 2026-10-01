import logging

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, ErrorEvent, Message

logger = logging.getLogger(__name__)

SORRY = "😔 Щось пішло не так. Спробуй ще раз або натисни /start."


def get_event_message(event: ErrorEvent) -> Message | None:
    """Дістає повідомлення, на яке можна відповісти, з будь-якого типу апдейту."""
    update = event.update

    if update.message is not None:
        return update.message

    if update.callback_query is not None:
        return update.callback_query.message

    return None


async def handle_error(event: ErrorEvent):
    """Останній рубіж: ловить усе, що не спіймали хендлери."""
    logger.exception(
        "Необроблена помилка в апдейті %s: %r",
        event.update.update_id,
        event.exception,
    )

    callback: CallbackQuery | None = event.update.callback_query

    if callback is not None:
        try:
            await callback.answer()
        except TelegramBadRequest:
            pass

    message = get_event_message(event)

    if message is None:
        return

    try:
        await message.answer(SORRY)
    except TelegramBadRequest:
        logger.warning("Не вдалося повідомити користувача про помилку")
