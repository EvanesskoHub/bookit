from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import select, func
from database import async_session
from models import UserBook, Book
from services.database import get_or_create_user
from keyboards.menu import main_menu

router = Router()

@router.message(Command("stats"))
@router.message(F.text == "📊 Статистика")
async def cmd_stats(message: Message):
    user = await get_or_create_user(message.from_user.id, message.from_user.username)
    
    async with async_session() as session:
        result = await session.execute(
            select(func.count(UserBook.id)).where(UserBook.user_id == user.id)
        )
        total_books = result.scalar() or 0
        
        if total_books == 0:
            await message.answer("📊 Пока нет статистики. Добавь книги через /addbook!", reply_markup=main_menu)
            return
        
        result = await session.execute(
            select(func.avg(UserBook.rating))
            .where(UserBook.user_id == user.id, UserBook.rating.isnot(None))
        )
        avg_rating = result.scalar()
        
        result = await session.execute(
            select(func.sum(UserBook.time_spent))
            .where(UserBook.user_id == user.id, UserBook.time_spent.isnot(None))
        )
        total_time = result.scalar() or 0
        
        result = await session.execute(
            select(Book.author, func.count(Book.id).label("count"))
            .join(UserBook, UserBook.book_id == Book.id)
            .where(UserBook.user_id == user.id)
            .group_by(Book.author)
            .order_by(func.count(Book.id).desc())
            .limit(1)
        )
        fav_author_row = result.one_or_none()
        fav_author = fav_author_row[0] if fav_author_row else "—"
        
        month_ago = datetime.now() - timedelta(days=30)
        result = await session.execute(
            select(func.count(UserBook.id))
            .where(UserBook.user_id == user.id, UserBook.created_at >= month_ago)
        )
        books_this_month = result.scalar() or 0
    
    avg_str = f"{avg_rating:.1f}" if avg_rating else "—"
    
    response = (
        f"📊 <b>Твоя статистика:</b>\n\n"
        f"📚 Всего прочитано: <b>{total_books}</b>\n"
        f"⭐ Средняя оценка: <b>{avg_str}</b> / 10\n"
        f"⏱ Общее время чтения: <b>{total_time}</b> дн.\n"
        f"🏆 Любимый автор: <b>{fav_author}</b>\n"
        f"📅 За последний месяц: <b>{books_this_month}</b> книг(и)"
    )
    
    await message.answer(response, parse_mode="HTML", reply_markup=main_menu)