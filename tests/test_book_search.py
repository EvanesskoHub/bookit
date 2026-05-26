import sys
import os
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'bot'))

from services.book_search import find_or_create_book
from database import engine, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DB = "sqlite:///:memory:"

@pytest.fixture
def db_setup():
    # Создаём тестовую БД с таблицами
    test_engine = create_engine(TEST_DB, echo=False)
    Base.metadata.create_all(test_engine)
    return test_engine

def test_find_or_create_book_new(db_setup, monkeypatch):
    # Переопределяем DATABASE_URL на тестовую БД
    import database
    monkeypatch.setattr(database, "DATABASE_URL", TEST_DB)
    
    # Пересоздаём engine для тестов
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    database.engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    database.async_session = async_sessionmaker(database.engine, class_=AsyncSession, expire_on_commit=False)

def test_book_status_values():
    from models import BookStatus
    assert BookStatus.READ.value == "прочитано"
    assert BookStatus.READING.value == "читаю"
    assert BookStatus.WANT_TO_READ.value == "хочу прочитать"

def test_user_model():
    from models import User
    user = User(telegram_id=777, username="bookworm")
    assert user.telegram_id == 777
    assert user.username == "bookworm"

def test_book_model():
    from models import Book
    book = Book(title="Война и мир", author="Толстой", year=1869)
    assert book.title == "Война и мир"
    assert book.author == "Толстой"
    assert book.year == 1869

def test_quote_model():
    from models import Quote
    quote = Quote(text="Быть или не быть")
    assert quote.text == "Быть или не быть"