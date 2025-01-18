import fastapi
from fastapi import HTTPException

from lifespan import lifespan
from schema import (
    AuthorSchema, UpdateAuthor, ItemId, StatusResponse, GenreSchema, BaseAuthor, 
    GetBook, AddBook, UpdateBook, CreateUser
)
from dependencies import SessionDependency
from models import Author, Book, Genre, User
from crud import get_item, add_item
import auth


app = fastapi.FastAPI(
    title = "Library RESTful API",
    version = "0.0.1",
    description = "A RESTful API for managing libraries",
    lifespan = lifespan
)

# Users

@app.post("/api/v1/register/", response_model=ItemId, tags=["users"])
async def register_user(user_data: CreateUser, session: SessionDependency):
    user = User(**user_data.model_dump())
    user.password = auth.hash_password(user.password)
    await add_item(session, user)
    return {"id": user.id}


# Authors

@app.get("/api/v1/authors/", response_model=list[AuthorSchema], tags=["authors"])
async def get_authors(session: SessionDependency):
    return []

@app.get("/api/v1/authors/{author_id}", response_model=AuthorSchema, tags=["authors"])
async def get_author(author_id: int, session: SessionDependency):
    author = await get_item(session, Author, author_id)
    return author.dict

@app.post("/api/v1/authors/", response_model=AuthorSchema, tags=["authors"])
async def create_author(author: AuthorSchema, session: SessionDependency):
    author = Author(**author.model_dump())
    await add_item(session, author)
    return author

@app.patch("/api/v1/authors/{author_id}", response_model=StatusResponse, tags=["authors"])
async def update_author(
    author_id: int,
    author: UpdateAuthor,
    session: SessionDependency
):
    db_author = await get_item(session, Author, author_id)
    for field, value in author.model_dump(exclude_unset=True).items():
        setattr(db_author, field, value)
    author = await add_item(session, db_author)
    return {"status": "ok"}

@app.delete("/api/v1/authors/{author_id}", response_model=StatusResponse, tags=["authors"])
async def delete_author(author_id: int, session: SessionDependency):
    author = await get_item(session, Author, author_id)
    await session.delete(author)
    await session.commit()
    return {"status": "deleted"}

# Genres

@app.get("/api/v1/genres/", response_model=list[GenreSchema], tags=["genres"])
async def get_genres(session: SessionDependency):
    return []

@app.post("/api/v1/genres/", response_model=GenreSchema, tags=["genres"])
async def create_genre(genre: GenreSchema, session: SessionDependency):
    genre = Genre(**genre.model_dump())
    await add_item(session, genre)
    return genre

# Books

@app.get("/api/v1/books/", response_model=list[GetBook], tags=["books"])
async def get_books(session: SessionDependency):
    return []

@app.get("/api/v1/books/{book_id}", response_model=GetBook, tags=["books"])
async def get_book(book_id: int, session: SessionDependency):
    book = await get_item(session, Book, book_id)
    return book.dict

@app.post("/api/v1/books/", response_model=GetBook, tags=["books"])
async def create_book(book: AddBook, session: SessionDependency):
    authors = []
    for author_id in book.authors:
        author = await get_item(session, Author, author_id)
        if author is None:
            raise HTTPException(status_code=404, detail=f"Author {author_id} not found")
        authors.append(author)
    genres = []
    for genre_id in book.genres:
        genre = await get_item(session, Genre, genre_id)
        if genre is None:
            raise HTTPException(status_code=404, detail=f"Genre {genre_id} not found")
        genres.append(genre)
    book = Book(
        title=book.title,
        description=book.description,
        release_year=book.release_year,
        authors=authors,
        genres=genres,
        available_stock=book.available_stock
    )
    await add_item(session, book)
    return book.dict

@app.patch("/api/v1/books/{book_id}", response_model=StatusResponse, tags=["books"])
async def update_book(
    book_id: int,
    book: UpdateBook,
    session: SessionDependency
):
    db_book = await get_item(session, Book, book_id)
    for field, value in book.model_dump(exclude_unset=True).items():
        setattr(db_book, field, value)
    book = await add_item(session, db_book)
    return {"status": "ok"}

@app.delete("/api/v1/books/{book_id}", response_model=StatusResponse, tags=["books"])
async def delete_book(book_id: int, session: SessionDependency):
    book = await get_item(session, Book, book_id)
    await session.delete(book)
    await session.commit()
    return {"status": "deleted"}