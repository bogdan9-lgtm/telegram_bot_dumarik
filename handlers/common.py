import json
import logging
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

import keyboards.inline as inline_kb
import keyboards.reply as reply_kb
from handlers.quiz import get_quiz_summary
from utils import image_path, load_message

router = Router(name="common")
logger = logging.getLogger(__name__)
USERS_FILE = Path(__file__).resolve().parent.parent / "users.json"


async def show_main_menu(message: Message, state: FSMContext) -> None:
    """Скидає будь-який активний сценарій і показує головне меню."""
    await state.clear()
    await message.answer_photo(
        photo=FSInputFile(image_path("main")),
        caption=load_message("main"),
        reply_markup=reply_kb.main_menu_kb,
    )


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext):
    user = message.from_user
    try:
        with USERS_FILE.open("r", encoding="utf-8") as f:
            users: dict = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}

    users[user.id] = {
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }

    with USERS_FILE.open("w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

    logger.info("Користувач %s натиснув /start", message.from_user.id)

    await show_main_menu(message, state)


@router.message(Command(commands=["help"]))
async def handle_help(message: Message):
    await message.answer(
        "Доступні команди:\n"
        "/start - Розпочати\n"
        "/help - Ця команда\n"
        "/random - Випадковий факт\n"
        "/gpt - Чат-бот\n"
        "/talk - Діалог з відомою особистістю\n"
        "/quiz - Квіз\n"
        "/resume - Допомога з резюме"
    )


@router.callback_query(F.data == inline_kb.CB_FINISH)
async def handle_finish(callback: CallbackQuery, state: FSMContext) -> None:
    """Кнопка «Закінчити» — за ТЗ працює так само, як /start."""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    summary = await get_quiz_summary(state)

    if summary is not None:
        await callback.message.answer(summary)

    await show_main_menu(callback.message, state)

