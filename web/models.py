from sqlalchemy import Column, Integer, BigInteger, String, Text, Float, Date, DateTime, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class BookStatus(str, enum.Enum):
    READ = "прочитано"
    READING = "читаю"
    WANT_TO_READ = "хочу прочитать"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())

    user_books = relationship("UserBook", back_populates="user")
    quotes = relationship("Quote", back_populates="user")

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    author = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    cover_url = Column(Text, nullable=True)
    year = Column(Integer, nullable=True)
    source = Column(String(50), nullable=True)
    source_id = Column(String(100), nullable=True)

    user_books = relationship("UserBook", back_populates="book")
    quotes = relationship("Quote", back_populates="book")

class UserBook(Base):
    __tablename__ = "user_books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    status = Column(SqlEnum(BookStatus), default=BookStatus.READ, nullable=False)
    rating = Column(Integer, nullable=True)
    review_text = Column(Text, nullable=True)
    time_spent = Column(Integer, nullable=True)
    started_date = Column(Date, nullable=True)
    finished_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="user_books")
    book = relationship("Book", back_populates="user_books")

class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="quotes")
    book = relationship("Book", back_populates="quotes")