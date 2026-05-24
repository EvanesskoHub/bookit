import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://bookit_user:bookit_pass_2024@db:5432/bookit_db")
DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC", "postgresql://bookit_user:bookit_pass_2024@db:5432/bookit_db")