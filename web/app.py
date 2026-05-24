from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker, joinedload
import os
from datetime import datetime, timedelta
import secrets

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))

# Подключение к БД (синхронное)
DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC", "postgresql://bookit_user:password@localhost:5432/bookit_db")
SessionLocal = sessionmaker(bind=engine)

# Импортируем модели
import sys
sys.path.insert(0, '/app')
from models import User, Book, UserBook, Quote, BookStatus

@app.route("/")
def home():
    return """
    <html>
    <head><title>BookIt Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        input { padding: 10px; width: 200px; font-size: 16px; }
        button { padding: 10px 20px; font-size: 16px; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #45a049; }
    </style>
    </head>
    <body>
    <div class="container">
        <h1>📚 BookIt Dashboard</h1>
        <p>Введи свой Telegram ID, чтобы посмотреть статистику:</p>
        <form action="/dashboard" method="get">
            <input type="number" name="user_id" placeholder="Telegram ID" required>
            <button type="submit">Открыть дашборд</button>
        </form>
    </div>
    </body>
    </html>
    """

@app.route("/dashboard")
def dashboard():
    user_id = request.args.get("user_id")
    if not user_id:
        return "Укажи user_id в параметрах: /dashboard?user_id=твой_id", 400
    
    session = SessionLocal()
    
    try:
        # Ищем пользователя по telegram_id
        user = session.query(User).filter(User.telegram_id == int(user_id)).first()
        if not user:
            return "Пользователь не найден. Сначала добавь книги через бота!", 404
        
        # Получаем книги пользователя
        user_books = session.query(UserBook).options(
            joinedload(UserBook.book)
        ).filter(UserBook.user_id == user.id).order_by(UserBook.created_at.desc()).all()
        
        # Статистика
        total_books = len(user_books)
        ratings = [ub.rating for ub in user_books if ub.rating]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        total_time = sum(ub.time_spent for ub in user_books if ub.time_spent) if user_books else 0
        
        # Любимый автор
        from collections import Counter
        authors = [ub.book.author for ub in user_books]
        fav_author = Counter(authors).most_common(1)[0][0] if authors else "—"
        
        # Книги по месяцам (для графика)
        books_by_month = {}
        for ub in user_books:
            month_key = ub.created_at.strftime("%Y-%m") if ub.created_at else "неизвестно"
            books_by_month[month_key] = books_by_month.get(month_key, 0) + 1
        # Сортируем по месяцам
        months_sorted = sorted(books_by_month.keys())
        months_labels = months_sorted
        months_data = [books_by_month[m] for m in months_sorted]
        
        # Распределение оценок
        rating_distribution = {i: 0 for i in range(1, 11)}
        for r in ratings:
            rating_distribution[r] += 1
        
        # Цитаты
        quotes = session.query(Quote).options(
            joinedload(Quote.book)
        ).filter(Quote.user_id == user.id).order_by(Quote.created_at.desc()).limit(10).all()
        
        # Облако слов из цитат (простейший вариант — топ-20 слов)
        from collections import Counter
        import re
        all_quote_text = " ".join([q.text for q in quotes])
        words = re.findall(r'[а-яёa-z]+', all_quote_text.lower(), re.IGNORECASE)
        stop_words = {"и", "в", "не", "на", "я", "с", "что", "а", "по", "как", "но", "к", "у", "же", "о", "из", "от", "за", "то", "все", "это", "так", "для", "он", "она", "его", "ее", "их", "бы", "мы", "ты", "вы", "мне", "меня", "тебя", "тебе", "нам", "вам", "или", "еще", "уже", "если", "когда", "даже", "там", "тут", "там", "был", "была", "было", "были", "очень", "просто", "только", "ещё", "этот", "эта", "это", "эти", "весь", "вся", "всё", "все"}
        filtered_words = [w for w in words if w not in stop_words and len(w) > 2]
        word_counts = Counter(filtered_words).most_common(30)
        
        return render_template(
            "dashboard.html",
            user=user,
            total_books=total_books,
            avg_rating=avg_rating,
            total_time=total_time,
            fav_author=fav_author,
            user_books=user_books,
            months_labels=months_labels,
            months_data=months_data,
            rating_distribution=rating_distribution,
            quotes=quotes,
            word_counts=word_counts
        )
    finally:
        session.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)