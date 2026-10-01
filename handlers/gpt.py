import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, Message
from aiogram.utils.chat_action import ChatActionSender

import keyboards.inline as inline_kb
import keyboards.reply as reply_kb
from catalog import FALLBACK
from filters import USER_TEXT
from gpt import ask
from utils import image_path, load_message, load_prompt

router = Router(name="gpt")
logger = logging.getLogger(__name__)


class GptStates(StatesGroup):
    dialog = State()


async def start_gpt_dialog(message: Message, state: FSMContext):
    """Вхід у режим GPT: чистий стан, картинка, підказка."""
    logger.info("Користувач %s увійшов у режим GPT", message.from_user.id)

    await state.clear()
    await state.set_state(GptStates.dialog)

    await message.answer_photo(
        photo=FSInputFile(image_path("gpt")),
        caption=load_message("gpt"),
        reply_markup=inline_kb.finish_kb,
    )


@router.message(Command('gpt'))
async def handle_command_gpt(message: Message, state: FSMContext):
    await start_gpt_dialog(message, state)


@router.message(F.text == reply_kb.BTN_GPT)
async def handle_gpt(message: Message, state: FSMContext):
    await start_gpt_dialog(message, state)


@router.message(GptStates.dialog, USER_TEXT)
async def handle_gpt_message(message: Message):
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        text = await ask(load_prompt("gpt"), message.text)

    if text is None:
        await message.answer(FALLBACK, reply_markup=inline_kb.finish_kb)
        return

    await message.answer(text, reply_markup=inline_kb.finish_kb)
