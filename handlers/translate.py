import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.chat_action import ChatActionSender

import keyboards.inline as inline_kb
import keyboards.reply as reply_kb
from catalog import FALLBACK, LANGUAGES
from filters import USER_TEXT
from gpt import ask
from utils import load_message, load_prompt

router = Router(name="translate")
logger = logging.getLogger(__name__)


class TranslateStates(StatesGroup):
    choosing_language = State()
    translating = State()


async def ask_language(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(TranslateStates.choosing_language)

    await message.answer(
        text=load_message("translate"),
        reply_markup=inline_kb.languages_kb()
    )



@router.message(Command("translate"))
@router.message(F.text == reply_kb.BTN_TRANSLATE)
async def handle_translate(message: Message, state: FSMContext):
    logger.info("Користувач %s почав переклад", message.from_user.id)
    await ask_language(message, state)



@router.callback_query(inline_kb.LanguageCallback.filter())
async def handle_choose_language(
    callback: CallbackQuery,
    callback_data: inline_kb.LanguageCallback,
    state: FSMContext,
):
    await callback.answer()

    code = callback_data.code

    if code not in LANGUAGES:
        await callback.message.answer("Такої мови вже немає. Почни заново: /translate")
        return

    await callback.message.edit_reply_markup(reply_markup=None)

    await state.update_data(code=code)
    await state.set_state(TranslateStates.translating)

    await callback.message.answer(f"Переклад на: <b>{LANGUAGES[code]}</b>")



@router.message(TranslateStates.translating, USER_TEXT)
async def handle_text_to_translate(message: Message, state: FSMContext):
    data = await state.get_data()
    code = data["code"]

    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        translated_text = await ask(
            system_prompt=load_prompt("translate").format(language=LANGUAGES[code]),
            user_message=message.text
        )

    if translated_text is None:
        await message.answer(FALLBACK, reply_markup=inline_kb.translate_kb)
        return


    await message.answer(
        text=translated_text,
        reply_markup=inline_kb.translate_kb
    )


@router.callback_query(F.data == inline_kb.CB_TRANSLATE_CHANGE)
async def handle_change_language(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    await ask_language(callback.message, state)


@router.message(TranslateStates.choosing_language, USER_TEXT)
async def handle_text_before_language(message: Message):
    await message.answer("Спершу обери мову кнопкою вище 👆")
