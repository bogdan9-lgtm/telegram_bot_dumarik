import logging

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.types import Message

import keyboards.reply as reply_kb

router = Router(name="fallback")
logger = logging.getLogger(__name__)


@router.message(StateFilter(None))
async def handle_unknown(message: Message):
    """Усе, що не зловив жоден сценарій. Роутер має бути останнім у списку."""
    logger.info("Користувач %s написав поза сценарієм", message.from_user.id)

    await message.answer(
        "Не зрозумів 🤔 Обери пункт меню нижче або введи команду.",
        reply_markup=reply_kb.main_menu_kb
    )
