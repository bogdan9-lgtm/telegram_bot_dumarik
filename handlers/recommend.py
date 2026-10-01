import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.chat_action import ChatActionSender

import keyboards.inline as inline_kb
import keyboards.reply as reply_kb
from catalog import FALLBACK, RECOMMEND_CATEGORIES
from filters import USER_TEXT
from gpt import ask
from utils import load_message, load_prompt

logger = logging.getLogger(__name__)
router = Router(name="recommend")


class RecommendStates(StatesGroup):
    choosing_category = State()
    preferences = State()


async def send_recommendation(message: Message, state: FSMContext):
    data = await state.get_data()
    category = data["category"]
    disliked = data["disliked"]

    prompt = (
        load_prompt("recommend")
        .format(
            category=RECOMMEND_CATEGORIES[category],
            preferences=data["preferences"],
            disliked="\n".join(f"- {title}" for title in disliked) or "(нічого)"
        )
    )

    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        text = await ask(system_prompt=prompt)

    if text is None:
        await message.answer(FALLBACK, reply_markup=inline_kb.finish_kb)
        return

    await state.update_data(last_title=text.splitlines()[0].strip())
    await message.answer(
        text=text,
        reply_markup=inline_kb.recommend_kb
    )


@router.message(Command("recommend"))
@router.message(F.text == reply_kb.BTN_RECOMMEND)
async def handle_recommend(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(RecommendStates.choosing_category)
    await message.answer(
        text=load_message("recommend"),
        reply_markup=inline_kb.choose_recommend_categories_kb()
    )


@router.callback_query(inline_kb.CategoryCallback.filter())
async def handle_choose_category(
        callback: CallbackQuery,
        callback_data: inline_kb.CategoryCallback,
        state: FSMContext
    ):

    category = callback_data.key

    if category not in RECOMMEND_CATEGORIES:
        await callback.message.answer("Такої категорії вже немає. Почни заново: /recommend")
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await state.set_state(RecommendStates.preferences)
    await state.update_data(category=category, disliked=[])

    await callback.message.answer(
        f"Категорія: <b>{RECOMMEND_CATEGORIES[category]}</b>\n"
        f"Які у тебе є додаткові вподобання? Напиши словами — наприклад «фантастика» або «щось легке»."
    )
    await callback.answer()


@router.message(RecommendStates.choosing_category, USER_TEXT)
async def handle_text_before_category(message: Message):
    await message.answer("Спершу обери категорію кнопкою вище 👆")



@router.message(RecommendStates.preferences, USER_TEXT)
async def handle_preferences(message: Message, state: FSMContext):
    await state.update_data(preferences=message.text)
    await send_recommendation(message, state)


@router.callback_query(F.data == inline_kb.CB_RECOMMEND_DISLIKE)
async def handle_dislike(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Гаразд, пошукаю інше")

    data = await state.get_data()

    if "preferences" not in data:
        await callback.message.answer("Підбір уже завершено. Почни заново: /recommend")
        return

    title = data.get("last_title")
    disliked = data.get("disliked", [])

    if title and title not in disliked:
        await state.update_data(disliked=[*disliked, title])
        logger.info("Користувач %s відкинув %r", callback.from_user.id, title)

    await callback.message.edit_reply_markup(reply_markup=None)
    await send_recommendation(callback.message, state)
