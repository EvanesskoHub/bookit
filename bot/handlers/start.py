from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from keyboards.menu import main_menu
import os

router = Router()

# URL твоего сервера — замени на свой IP
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "📚 Привет! Я BookIt — твой читательский дневник.\n\n"
        "Используй меню снизу или команды:\n"
        "/addbook — добавить книгу\n"
        "/books — список книг\n"
        "/stats — статистика\n"
        "/dashboard — веб-дашборд\n"
        "/addquote — добавить цитату\n"
        "/quotes — цитаты\n"
        "/help — помощь",
        reply_markup=main_menu
    )

@router.message(Command("help"))
@router.message(F.text == "❓ Помощь")
async def cmd_help(message: Message):
    await message.answer(
        "📚 BookIt — твой читательский дневник\n\n"
        "✍️ Добавить книгу — /addbook\n"
        "📚 Мои книги — /books\n"
        "📊 Статистика — /stats\n"
        "📊 Дашборд — /dashboard (откроется в браузере)\n"
        "💬 Добавить цитату — /addquote\n"
        "📝 Мои цитаты — /quotes\n\n"
        "Или используй кнопки меню снизу 👇",
        reply_markup=main_menu
    )

@router.message(Command("dashboard"))
@router.message(F.text == "📊 Дашборд")
async def cmd_dashboard(message: Message):
    user_id = message.from_user.id
    dashboard_url = f"{SERVER_URL}/dashboard?user_id={user_id}"
    await message.answer(
        f"📊 <a href='{dashboard_url}'>Открыть дашборд</a>",
        parse_mode="HTML",
        reply_markup=main_menu
    )