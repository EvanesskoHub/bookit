# 📚 BookIt — Reading Journal

[![Tests](https://github.com/EvanesskoHub/bookit/actions/workflows/tests.yml/badge.svg)](https://github.com/EvanesskoHub/bookit/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-green)](https://github.com/aiogram/aiogram)
[![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)](https://docs.docker.com/compose/)

A Telegram bot + web dashboard for tracking your reading.  
Add books with cover search, rate them, save quotes, and view beautiful statistics.

**Pet project created as part of learning Python development.**

## ✨ Features

- 📖 **Add books** with Google Books / Open Library search
- 🖼 **Cover images** — auto-search + manual upload
- ⭐ **Ratings** (1-10) and reviews
- 💬 **Quotes** — save and browse
- 📊 **Stats** — /stats command with key metrics
- 📈 **Web dashboard** — Chart.js graphs, book shelf, word cloud
- 🗄 **PostgreSQL** — async via SQLAlchemy 2.0
- 🐳 **Docker** — easy deployment with docker compose

## 🛠 Tech Stack

| Technology       | Description                          |
|------------------|--------------------------------------|
| Python 3.11      | Core language                        |
| Aiogram 3.x      | Telegram Bot API framework           |
| Flask 3.0        | Web dashboard                        |
| PostgreSQL 15    | Database                             |
| SQLAlchemy 2.0   | Async ORM                            |
| Chart.js         | Graphs in dashboard                  |
| Jinja2           | HTML templates                       |
| Docker Compose   | Container orchestration              |

## ⚙️ Installation & Launch

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- A Telegram bot token from @BotFather

### 1. Clone the repository

`git clone https://github.com/EvanesskoHub/bookit.git`

`cd bookit`

### 2. Configure environment

`cp .env.example .env`

Edit `.env` and fill in your tokens.

### 3. Run with Docker

`docker compose up -d`

The bot and dashboard will start. Access the dashboard at `http://localhost:8000`.

## 📁 Project Structure

bookit/
├── bot/ # Telegram bot
│ ├── main.py # Entry point
│ ├── config.py # Configuration
│ ├── database.py # Async DB connection
│ ├── models.py # SQLAlchemy models
│ ├── Dockerfile
│ ├── requirements.txt
│ ├── alembic.ini # Database migrations config
│ ├── alembic/ # Migration files
│ ├── handlers/ # Bot command handlers
│ │ ├── start.py
│ │ ├── books.py
│ │ ├── quotes.py
│ │ └── stats.py
│ ├── services/ # Business logic
│ │ ├── database.py
│ │ └── book_search.py
│ └── keyboards/ # Telegram keyboards
│ └── menu.py
├── web/ # Web dashboard
│ ├── app.py # Flask application
│ ├── models.py # SQLAlchemy models
│ ├── Dockerfile
│ ├── requirements.txt
│ └── templates/
│ └── dashboard.html # Dashboard with Chart.js
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md


## 📸 Screenshots

*(Add screenshots here)*

## 📝 Notes

This project demonstrates:

- Async Python with aiogram + SQLAlchemy
- Web dashboard with Flask + Chart.js
- External API integration (Google Books, Open Library)
- Full-text search with PostgreSQL
- Docker multi-container deployment
- Environment variable management

---

💬 **Contact:** [Telegram](https://t.me/Evanessko) | [Email](mailto:zupinka2004@mail.ru)

---

## 📚 Русская версия / Russian

**BookIt** — читательский дневник: Telegram-бот + веб-дашборд.

**Функции:** добавление книг с поиском обложек, оценки, цитаты, статистика, графики Chart.js, облако слов.

**Стек:** Python, Aiogram, Flask, PostgreSQL, Docker, SQLAlchemy, Chart.js.

**Контакты:** [Telegram](https://t.me/Evanessko) | [Email](mailto:zupinka2004@mail.ru)