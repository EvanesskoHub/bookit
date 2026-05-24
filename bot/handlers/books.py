from datetime import date
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from database import async_session
from models import User, Book, UserBook, BookStatus
from services.database import get_or_create_user
from services.book_search import find_or_create_book
from keyboards.menu import main_menu, skip_button


router = Router()

class AddBook(StatesGroup):
    waiting_for_title = State()
    waiting_for_cover = State()
    waiting_for_rating = State()
    waiting_for_review = State()
    waiting_for_time = State()

def escape_md(text: str) -> str:
    chars = "_*[]()~`>#+-=|{}.!"
    for char in chars:
        text = text.replace(char, f"\\{char}")
    return text

@router.message(Command("addbook"))
@router.message(F.text == "✍️ Добавить книгу")
async def cmd_addbook(message: Message, state: FSMContext):
    await message.answer("📖 Введи название книги и автора (например: «Мастер и Маргарита, Булгаков»):")
    await state.set_state(AddBook.waiting_for_title)

@router.message(AddBook.waiting_for_title)
async def process_title(message: Message, state: FSMContext):
    text = message.text.strip()
    
    if "," in text:
        parts = text.split(",", 1)
        title = parts[0].strip()
        author = parts[1].strip()
    else:
        title = text
        author = None
    
    await message.answer(f"🔍 Ищу книгу: «{title}»...")
    
    try:
        book, need_cover = await find_or_create_book(title, author)
        user = await get_or_create_user(message.from_user.id, message.from_user.username)
        
        async with async_session() as session:
            result = await session.execute(
                select(UserBook).where(UserBook.user_id == user.id, UserBook.book_id == book.id)
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                await message.answer(f"📚 Книга «{book.title}» уже есть в твоём списке!", reply_markup=main_menu)
                await state.clear()
                return
            
            user_book = UserBook(
                user_id=user.id,
                book_id=book.id,
                status=BookStatus.READ,
                finished_date=date.today()
            )
            session.add(user_book)
            await session.commit()
            await session.refresh(user_book)
            await state.update_data(book_id=book.id, user_book_id=user_book.id)
        
        response = f"✅ Книга добавлена: «{book.title}» — {book.author}\n"
        if book.year:
            response += f"📅 Год: {book.year}\n"
        if book.description:
            response += f"📝 {book.description[:300]}...\n"
        
        await message.answer(response)
        
        if need_cover:
            await message.answer(
                "🖼 У этой книги нет обложки. Отправь фото или нажми «Пропустить»:",
                reply_markup=skip_button("skip_cover")
            )
            await state.set_state(AddBook.waiting_for_cover)
        else:
            await message.answer(
                "⭐ Поставь оценку от 1 до 10:",
                reply_markup=skip_button("skip_rating")
            )
            await state.set_state(AddBook.waiting_for_rating)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
        await state.clear()

@router.callback_query(F.data == "skip_cover")
async def skip_cover(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "⭐ Поставь оценку от 1 до 10:",
        reply_markup=skip_button("skip_rating")
    )
    await state.set_state(AddBook.waiting_for_rating)
    await callback.answer()

@router.message(AddBook.waiting_for_cover, F.photo)
async def process_cover_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    book_id = data.get("book_id")
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file.file_path}"
    
    async with async_session() as session:
        result = await session.execute(select(Book).where(Book.id == book_id))
        book = result.scalar_one_or_none()
        if book:
            book.cover_url = file_url
            await session.commit()
    
    await message.answer("✅ Обложка сохранена!")
    await message.answer(
        "⭐ Поставь оценку от 1 до 10:",
        reply_markup=skip_button("skip_rating")
    )
    await state.set_state(AddBook.waiting_for_rating)

@router.message(AddBook.waiting_for_cover)
async def process_cover_text(message: Message):
    await message.answer("Отправь фото обложки или нажми «Пропустить».")

@router.callback_query(F.data == "skip_rating")
async def skip_rating(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "📝 Напиши рецензию:",
        reply_markup=skip_button("skip_review")
    )
    await state.set_state(AddBook.waiting_for_review)
    await callback.answer()

@router.message(AddBook.waiting_for_rating)
async def process_rating(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    
    try:
        rating = int(text)
        if 1 <= rating <= 10:
            async with async_session() as session:
                result = await session.execute(
                    select(UserBook).where(UserBook.id == data.get("user_book_id"))
                )
                user_book = result.scalar_one_or_none()
                if user_book:
                    user_book.rating = rating
                    await session.commit()
            await message.answer(f"✅ Оценка {rating}/10 сохранена!")
        else:
            await message.answer("Оценка должна быть от 1 до 10:")
            return
    except ValueError:
        await message.answer("Введи число от 1 до 10:")
        return
    
    await message.answer(
        "📝 Напиши рецензию:",
        reply_markup=skip_button("skip_review")
    )
    await state.set_state(AddBook.waiting_for_review)

@router.callback_query(F.data == "skip_review")
async def skip_review(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "⏱ Сколько дней читал(а) книгу?",
        reply_markup=skip_button("skip_time")
    )
    await state.set_state(AddBook.waiting_for_time)
    await callback.answer()

@router.message(AddBook.waiting_for_review)
async def process_review(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    
    async with async_session() as session:
        result = await session.execute(
            select(UserBook).where(UserBook.id == data.get("user_book_id"))
        )
        user_book = result.scalar_one_or_none()
        if user_book:
            user_book.review_text = text
            await session.commit()
    await message.answer("✅ Рецензия сохранена!")
    
    await message.answer(
        "⏱ Сколько дней читал(а) книгу?",
        reply_markup=skip_button("skip_time")
    )
    await state.set_state(AddBook.waiting_for_time)

@router.callback_query(F.data == "skip_time")
async def skip_time(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "🎉 Книга сохранена!\n\n"
        "📚 Мои книги — /books\n"
        "📊 Статистика — /stats",
        reply_markup=main_menu
    )
    await state.clear()
    await callback.answer()

@router.message(AddBook.waiting_for_time)
async def process_time(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    
    try:
        days = int(text)
        async with async_session() as session:
            result = await session.execute(
                select(UserBook).where(UserBook.id == data.get("user_book_id"))
            )
            user_book = result.scalar_one_or_none()
            if user_book:
                user_book.time_spent = days
                await session.commit()
        await message.answer(f"✅ Время чтения: {days} дн.")
    except ValueError:
        await message.answer("Введи число дней:")
        return
    
    await message.answer(
        "🎉 Книга полностью сохранена!\n\n"
        "📚 Мои книги — /books\n"
        "📊 Статистика — /stats",
        reply_markup=main_menu
    )
    await state.clear()

@router.message(Command("books"))
@router.message(F.text == "📚 Мои книги")
async def cmd_books(message: Message):
    user = await get_or_create_user(message.from_user.id, message.from_user.username)
    
    async with async_session() as session:
        result = await session.execute(
            select(UserBook)
            .options(joinedload(UserBook.book))
            .where(UserBook.user_id == user.id)
            .order_by(UserBook.created_at.desc())
        )
        user_books = result.unique().scalars().all()
    
    if not user_books:
        await message.answer("📚 У тебя пока нет книг. Добавь через /addbook!", reply_markup=main_menu)
        return
    
    response = "📚 <b>Твои книги:</b>\n\n"
    for i, ub in enumerate(user_books, 1):
        book = ub.book
        rating_str = f" — {ub.rating}/10" if ub.rating else ""
        response += f"{i}. 📖 <b>{book.title}</b> — {book.author}{rating_str}\n"
    
    await message.answer(response, parse_mode="HTML", reply_markup=main_menu)