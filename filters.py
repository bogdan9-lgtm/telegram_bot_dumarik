from aiogram import F

from keyboards.reply import MENU_BUTTONS

USER_TEXT = F.text & ~F.text.startswith("/") & ~F.text.in_(MENU_BUTTONS)