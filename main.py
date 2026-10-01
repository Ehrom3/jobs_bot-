import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from dotenv import load_dotenv

from connection import create_table
from service import get_user, save_user, get_jobs
from keyboards import main_menu, category_menu, job_apply_keyboard
from states import router as state_router
from callbacks import router as callback_router

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    user = await get_user(message.from_user.id)

    if not user:
        await save_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.full_name
        )

    await message.answer(
        f"👋 Привет, {message.from_user.full_name}!\n"
        "Это Jobs Bot. Здесь можно публиковать вакансии и откликаться на них.",
        reply_markup=main_menu()
    )


@dp.message(Command("help"))
@dp.message(F.text == "❓ Help")
async def help_command(message: Message):
    await message.answer(
        "❓ Jobs Bot — бот для вакансий.\n\n"
        "💼 Вакансии — посмотреть опубликованные работы.\n"
        "➕ Добавить работу — создать новую вакансию.\n"
        "📂 Категории — показать, добавить, изменить или удалить категории.\n"
        "📨 Откликнуться — отправить отклик автору вакансии.\n\n"
        "При отклике автор вакансии получает сообщение с данными кандидата."
    )


@dp.message(F.text == "📂 Категории")
async def categories(message: Message):
    await message.answer(
        "📂 Управление категориями:",
        reply_markup=category_menu()
    )


@dp.message(F.text == "💼 Вакансии")
async def jobs(message: Message):
    rows = await get_jobs()

    if not rows:
        await message.answer("Пока нет опубликованных вакансий.")
        return

    for job in rows:
        category = job["cotegory_name"] or "Без категории"
        text = (
            f"💼 {job['title']}\n\n"
            f"📂 Категория: {category}\n"
            f"💰 Зарплата: {job['salary']}\n"
            f"📝 Описание: {job['discription'] or 'Нет описания'}"
        )

        await message.answer(
            text,
            reply_markup=job_apply_keyboard(job["jobs_id"])
        )


async def main():
    if not BOT_TOKEN:
        print("BOT_TOKEN не найден в .env")
        return

    print("Start Bot")

    dp.include_router(state_router)
    dp.include_router(callback_router)

    await create_table()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
