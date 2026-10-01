import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config import settings
from handlers import routers
from handlers.errors import handle_error
from middlewares.throttling import ThrottlingMiddleware

logger = logging.getLogger(__name__)

async def set_commands(bot: Bot) -> None:
    await bot.set_my_commands([
        BotCommand(command="start", description="Головне меню"),
        BotCommand(command="help", description="Допомога"),
        BotCommand(command="random", description="Випадковий факт"),
        BotCommand(command="gpt", description="Питання до ChatGPT"),
        BotCommand(command="talk", description="Діалог з відомою особистістю"),
        BotCommand(command="quiz", description="Квіз"),
        BotCommand(command="resume", description="Допомога з резюме"),
    ])

def setup_logging() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)


async def main():
    setup_logging()

    bot = Bot(
        settings.BOT_API_KEY,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    await set_commands(bot)

    dp.include_routers(*routers)
    dp.error.register(handle_error)

    throttling = ThrottlingMiddleware(rate_limit=1.0)
    dp.message.outer_middleware(throttling)
    dp.callback_query.outer_middleware(throttling)

    print("Запускаємо бота...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Зупинка бота...")