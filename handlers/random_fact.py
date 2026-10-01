import logging
import random

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.utils.chat_action import ChatActionSender

import keyboards.reply as reply_kb
from catalog import FACT_TOPICS, FALLBACK
from gpt import ask
from keyboards.inline import CB_RANDOM_MORE, random_fact_kb
from utils import image_path, load_message, load_prompt

router = Router(name="random_fact")
logger = logging.getLogger(__name__)


class RandomFactStates(StatesGroup):
    active = State()


async def send_fact(message: Message):
    """Питає в моделі факт на випадкову тему і надсилає його з кнопками."""
    prompt = load_prompt("random").format(topic=random.choice(FACT_TOPICS))

    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        text = await ask(prompt)

    if text is None:
        await message.answer(FALLBACK, reply_markup=random_fact_kb)
        return

    await message.answer(text, reply_markup=random_fact_kb)


@router.message(Command("random"))
@router.message(F.text == reply_kb.BTN_FACT)
async def handle_fact(message: Message, state: FSMContext):
    logger.info("Користувач %s попросив факт", message.from_user.id)

    await state.clear()
    await state.set_state(RandomFactStates.active)
    await message.answer_photo(
        photo=FSInputFile(image_path("random")),
        caption=load_message("random"),
    )

    await send_fact(message)


@router.callback_query(F.data == CB_RANDOM_MORE)
async def handle_more_facts(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    await send_fact(callback.message)
