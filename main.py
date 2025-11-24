from src.data.DeepSeekClient import DeepSeekClient
from src.data.UserRepository import UserRepository
from src.data.JsonLlmLogger import JsonLlmLogger
from src.data.get_llm_config_from_env import get_llm_config_from_env
from src.core.EnglishTeacher import EnglishTeacher
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

english_teacher = EnglishTeacher(
    UserRepository(),
    DeepSeekClient(
        get_llm_config_from_env(),
        JsonLlmLogger()
    )
)

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    welcome_text = (
        "👋 Welcome to your English teacher bot!\n\n"
        "I'll help you improve your English skills. "
        "Just start chatting with me in English and I'll respond, "
        "correct your mistakes, and help you learn!\n\n"
        "Type anything to get started!"
    )
    await message.answer(welcome_text)


@router.message(F.text)
async def message_handler(message: Message):
    user_id = message.from_user.id
    user_message = message.text

    try:
        bot_response = await english_teacher.get_answer(user_id, user_message)
        await message.answer(bot_response)

    except Exception as e:
        error_message = "Sorry, I encountered an error. Please try again."
        print(f"Error processing message: {e}")
        await message.answer(error_message)


async def main():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

    bot = Bot(token=bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    print("Bot is starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
