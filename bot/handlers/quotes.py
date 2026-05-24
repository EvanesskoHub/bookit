from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from database import async_session
from models import Quote, UserBook
from services.database import get_or_create_user
from keyboards.menu import main_menu

router = Router()

class AddQuote(StatesGroup):
    waiting_for_book = State()
    waiting_for_text = State()

def escape_md(text: str) -> str:
    chars = "_*[]()~`>#+-=|{}.!"
    for char in chars:
        text = text.replace(char, f"\\{char}")
    return text

async def get_user_books_for_select(user_id: int) -> list[dict]:
    async with async_session() as session:
        result = await session.execute(
            select(UserBook)
            .options(joinedload(UserBook.book))
            .where(UserBook.user_id == user_id)
            .order_by(UserBook.created_at.desc())
        )
        user_books = result.unique().scalars().all()
        return [
            {"id": ub.book_id, "title": ub.book.title, "author": ub.book.author}
            for ub in user_books
        ]

@router.message(Command("addquote"))
@router.message(F.text == "💬 Цитаты")
async def cmd_addquote(message: Message, state: FSMContext):
    # Проверяем, есть ли уже активное состояние
    current_state = await state.get_state()
    if current_state and current_state.startswith("AddQuote"):
        # Уже в процессе добавления цитаты
        await message.answer("Ты уже добавляешь цитату. Отправь текст или нажми /start для сброса.")
        return
    
    user = await get_or_create_user(message.from_user.id, message.from_user.username)
    books = await get_user_books_for_select(user.id)
    
    if not books:
        await message.answer("📚 Сначала добавь книги через /addbook!", reply_markup=main_menu)
        return
    
    response = "📖 Выбери книгу (отправь номер):\n\n"
    for i, b in enumerate(books, 1):
        response += f"{i}. «{b['title']}» — {b['author']}\n"
    
    await message.answer(response)
    await state.update_data(books_list=books)
    await state.set_state(AddQuote.waiting_for_book)

@router.message(AddQuote.waiting_for_book)
async def process_quote_book(message: Message, state: FSMContext):
    data = await state.get_data()
    books = data.get("books_list", [])
    
    try:
        index = int(message.text.strip()) - 1
        if 0 <= index < len(books):
            book = books[index]
            await state.update_data(quote_book_id=book["id"], quote_book_title=book["title"])
            await message.answer(f"📝 Отправь цитату из книги «{book['title']}»:")
            await state.set_state(AddQuote.waiting_for_text)
        else:
            await message.answer(f"Введи номер от 1 до {len(books)}:")
    except ValueError:
        await message.answer(f"Введи номер цифрой (от 1 до {len(books)}):")

@router.message(AddQuote.waiting_for_text)
async def process_quote_text(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    user = await get_or_create_user(message.from_user.id, message.from_user.username)
    
    async with async_session() as session:
        quote = Quote(
            user_id=user.id,
            book_id=data["quote_book_id"],
            text=text
        )
        session.add(quote)
        await session.commit()
    
    await message.answer(f"✅ Цитата сохранена!", reply_markup=main_menu)
    await state.clear()

@router.message(Command("quotes"))
async def cmd_quotes(message: Message):
    user = await get_or_create_user(message.from_user.id, message.from_user.username)
    
    async with async_session() as session:
        result = await session.execute(
            select(Quote)
            .options(joinedload(Quote.book))
            .where(Quote.user_id == user.id)
            .order_by(Quote.created_at.desc())
            .limit(10)
        )
        quotes = result.unique().scalars().all()
    
    if not quotes:
        await message.answer("📝 У тебя пока нет цитат. Используй 💬 Цитаты в меню!", reply_markup=main_menu)
        return
    
    response = "📝 <b>Твои цитаты:</b>\n\n"
    for i, q in enumerate(quotes, 1):
        quote_text = q.text[:100] + ("..." if len(q.text) > 100 else "")
        response += f"{i}. «{quote_text}»\n📖 <b>{q.book.title}</b>\n\n"
    
    await message.answer(response, parse_mode="HTML", reply_markup=main_menu)