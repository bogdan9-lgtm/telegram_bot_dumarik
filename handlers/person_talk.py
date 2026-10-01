import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.utils.chat_action import ChatActionSender

import keyboards.inline as inline_kb
import keyboards.reply as reply_kb
from catalog import FALLBACK, PERSONS
from config import settings
from filters import USER_TEXT
from gpt import ask_history
from utils import image_path, load_message, load_prompt

logger = logging.getLogger(__name__)
router = Router(name="person_talk")


class TalkStates(StatesGroup):
    choosing = State()
    dialog = State()


@router.message(Command("talk"))
@router.message(F.text == reply_kb.BTN_TALK)
async def handle_talk(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(TalkStates.choosing)
    await message.answer_photo(
        photo=FSInputFile(image_path("talk")),
        caption=load_message("talk"),
        reply_markup=inline_kb.talk_kb()
    )


@router.callback_query(inline_kb.TalkCallback.filter())
async def handle_choose_person(
        callback: CallbackQuery,
        callback_data: inline_kb.TalkCallback,
        state: FSMContext
    ):

    person = callback_data.person

    if person not in PERSONS:
        await callback.message.answer("Цієї особистості вже немає. Обери іншу: /talk")
        return


    await callback.message.edit_reply_markup(None)
    await state.set_state(TalkStates.dialog)
    await state.set_data({"person": person, "history": []})

    logger.info("Користувач %s говорить з %s", callback.from_user.id, person)

    await callback.message.answer_photo(
        photo=FSInputFile(image_path(f"talk_{person}")),
        caption=f"Ти говориш з <b>{PERSONS[person]}</b>. Напиши перше повідомлення 👇",
        reply_markup=inline_kb.finish_kb
    )
    await callback.answer()


@router.message(TalkStates.choosing, USER_TEXT)
async def handle_text_before_person(message: Message):
    await message.answer("Спершу обери співрозмовника кнопкою вище 👆")


"""
[
    {"role": "system",    "content": "Ти — Дж.Р.Р. Толкін..."},        # хто ти
    {"role": "user",      "content": "Мене звати Віталік. Чому ви..."},# що сказали тобі
    {"role": "assistant", "content": "Радий познайомитися, Віталіку..."},# що ТИ відповів
    {"role": "user",      "content": "Як мене звати?"},                # нове питання
]
"""

@router.message(TalkStates.dialog, USER_TEXT)
async def handle_talk_message(message: Message, state: FSMContext):
    data = await state.get_data()
    person = data["person"]
    history = [*data["history"], {"role": "user", "content": message.text}]

    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        text = await ask_history(
            system_prompt=load_prompt(f"talk_{person}"),
            history=history
        )

    if text is None:
        await message.answer(FALLBACK, reply_markup=inline_kb.finish_kb)
        return

    history.append({"role": "assistant", "content": text})
    await state.update_data(history=history[-settings.MAX_GPT_HISTORY:])

    await message.answer(
        text=text,
        reply_markup=inline_kb.finish_kb
    )