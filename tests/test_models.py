import sys
import os
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'bot'))

from models import Base, User, Book, Quote, BookStatus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Обычная синхронная SQLite для тестов
TEST_DB = "sqlite:///:memory:"

@pytest.fixture
def session():
    engine = create_engine(TEST_DB, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.close()
    engine.dispose()

def test_create_user(session):
    user = User(telegram_id=12345, username="testuser")
    session.add(user)
    session.commit()
    assert user.id is not None
    assert user.telegram_id == 12345
    assert user.username == "testuser"

def test_create_book(session):
    book = Book(title="Мастер и Маргарита", author="Булгаков")
    session.add(book)
    session.commit()
    assert book.id is not None
    assert book.title == "Мастер и Маргарита"
    assert book.author == "Булгаков"

def test_create_quote(session):
    user = User(telegram_id=12345)
    book = Book(title="Тестовая книга", author="Автор")
    session.add_all([user, book])
    session.commit()

    quote = Quote(user_id=user.id, book_id=book.id, text="Тестовая цитата")
    session.add(quote)
    session.commit()
    assert quote.id is not None
    assert quote.text == "Тестовая цитата"

def test_book_status_enum():
    assert BookStatus.READ.value == "прочитано"
    assert BookStatus.READING.value == "читаю"
    assert BookStatus.WANT_TO_READ.value == "хочу прочитать"