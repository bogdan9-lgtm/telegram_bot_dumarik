import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

import keyboards.reply as reply_kb
from filters import USER_TEXT

router = Router(name="resume")
logger = logging.getLogger(__name__)


class ResumeStates(StatesGroup):
	education = State()
	experience = State()
	skills = State()


async def start_resume(message: Message, state: FSMContext) -> None:
	await state.clear()
	await state.set_state(ResumeStates.education)
	logger.info("Користувач %s почав створення резюме", message.from_user.id)
	await message.answer(
		"Допоможу скласти резюме. Напиши інформацію про освіту "
		"(навчальний заклад, спеціальність, роки навчання). Якщо хочеш пропустити розділ, надішли «-»."
	)


@router.message(Command("resume"))
@router.message(F.text == reply_kb.BTN_RESUME)
async def handle_resume(message: Message, state: FSMContext):
	await start_resume(message, state)


@router.message(ResumeStates.education, USER_TEXT)
async def handle_education(message: Message, state: FSMContext):
	await state.update_data(education=message.text)
	await state.set_state(ResumeStates.experience)
	await message.answer(
		"Опиши досвід роботи: посади, компанії, періоди та основні обов'язки. "
		"Якщо досвіду ще немає, надішли «-»."
	)


@router.message(ResumeStates.experience, USER_TEXT)
async def handle_experience(message: Message, state: FSMContext):
	await state.update_data(experience=message.text)
	await state.set_state(ResumeStates.skills)
	await message.answer("Переліч свої професійні та особисті навички.")


@router.message(ResumeStates.skills, USER_TEXT)
async def handle_skills(message: Message, state: FSMContext):
	await state.update_data(skills=message.text)
	data = await state.get_data()

	resume = (
		"РЕЗЮМЕ\n\n"
		"Освіта\n"
		f"{data['education']}\n\n"
		"Досвід роботи\n"
		f"{data['experience']}\n\n"
		"Навички\n"
		f"{data['skills']}"
	)

	logger.info("Користувач %s завершив створення резюме", message.from_user.id)
	await state.clear()
	await message.answer(
		resume,
		parse_mode=None,
		reply_markup=reply_kb.main_menu_kb,
	)


@router.message(ResumeStates.education, F.text.startswith("/"))
@router.message(ResumeStates.experience, F.text.startswith("/"))
@router.message(ResumeStates.skills, F.text.startswith("/"))
async def handle_command_during_resume(message: Message):
	await message.answer("Спершу заверши створення резюме або почни заново командою /resume.")
