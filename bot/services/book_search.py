import logging
import urllib.parse
import aiohttp
from sqlalchemy import select
from database import async_session
from models import Book
from config import GOOGLE_BOOKS_API_KEY

logger = logging.getLogger(__name__)

async def search_book_google(query: str) -> dict | None:
    if not GOOGLE_BOOKS_API_KEY:
        return None
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": query, "langRestrict": "ru", "maxResults": 1, "key": GOOGLE_BOOKS_API_KEY}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    items = data.get("items", [])
                    if items:
                        info = items[0]["volumeInfo"]
                        isbn = None
                        for ident in info.get("industryIdentifiers", []):
                            if ident.get("type") in ("ISBN_13", "ISBN_10"):
                                isbn = ident.get("identifier")
                                break
                        return {
                            "title": info.get("title", ""),
                            "author": ", ".join(info.get("authors", [])),
                            "description": info.get("description", ""),
                            "cover_url": info.get("imageLinks", {}).get("thumbnail", ""),
                            "year": info.get("publishedDate", "")[:4],
                            "source": "google",
                            "source_id": items[0].get("id", ""),
                            "isbn": isbn
                        }
    except Exception as e:
        logger.error(f"Google Books API error: {e}")
    return None

async def get_cover_openlibrary(title: str = None, author: str = None, isbn: str = None) -> str | None:
    if isbn:
        url = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url) as resp:
                    if resp.status == 200:
                        return url
        except:
            pass
    if title:
        encoded_title = urllib.parse.quote(title.replace(' ', '_'))
        url = f"https://covers.openlibrary.org/b/title/{encoded_title}-M.jpg"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url) as resp:
                    if resp.status == 200:
                        return url
        except:
            pass
    if title and author:
        try:
            search_url = f"https://openlibrary.org/search.json?title={urllib.parse.quote(title)}&author={urllib.parse.quote(author)}&limit=1"
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        docs = data.get("docs", [])
                        if docs and docs[0].get("cover_i"):
                            return f"https://covers.openlibrary.org/b/id/{docs[0]['cover_i']}-M.jpg"
        except:
            pass
    return None

async def find_or_create_book(title: str, author: str = None) -> tuple[Book, bool]:
    async with async_session() as session:
        query = select(Book).where(Book.title.ilike(f"%{title}%"))
        if author:
            query = query.where(Book.author.ilike(f"%{author}%"))
        result = await session.execute(query)
        book = result.scalar_one_or_none()
        
        if book:
            return book, not book.cover_url
        
        google_data = await search_book_google(f"{title} {author}" if author else title)
        
        cover_url = None
        if google_data:
            cover_url = google_data.get("cover_url")
            if not cover_url:
                cover_url = await get_cover_openlibrary(
                    title=google_data.get("title"), 
                    author=google_data.get("author"),
                    isbn=google_data.get("isbn")
                )
        else:
            cover_url = await get_cover_openlibrary(title=title, author=author)
        
        book = Book(
            title=google_data["title"] if google_data else title,
            author=google_data["author"] if google_data else (author or "Неизвестен"),
            description=google_data.get("description") if google_data else None,
            cover_url=cover_url,
            year=int(google_data["year"]) if google_data and google_data.get("year") else None,
            source=google_data.get("source") if google_data else "manual",
            source_id=google_data.get("source_id") if google_data else None
        )
        session.add(book)
        await session.commit()
        await session.refresh(book)
        
        return book, not book.cover_url