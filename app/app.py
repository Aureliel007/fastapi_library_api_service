import fastapi
from fastapi import HTTPException
from sqlalchemy import select

from lifespan import lifespan
from schema import (
    AuthorSchema, UpdateAuthor, ItemId, StatusResponse, GenreSchema, BaseAuthor, 
    GetBook, AddBook, UpdateBook, CreateUser, BaseUser, GetUser, UpdateUser,
    CreateAuthor, GetUserDetails
)
from dependencies import (
    SessionDependency, UserAdminDependency, FiltersDependency, TokenDependency
)
from models import Author, Book, Genre, User, UserRole
from crud import get_item, add_item
import auth


app = fastapi.FastAPI(
    title = "Library RESTful API",
    version = "0.0.1",
    description = "A RESTful API for managing libraries",
    lifespan = lifespan
)

# Auth

@app.post("/api/v1/register/", response_model=ItemId, tags=["auth"])
async def register_user(user_data: CreateUser, session: SessionDependency):
    user = User(**user_data.model_dump())
    user.password = auth.hash_password(user.password)
    await add_item(session, user)
    return {"id": user.id}

@app.post("/api/v1/admin_register/", response_model=ItemId, tags=["auth"])
async def admin_register(user_data: CreateUser, session: SessionDependency):
    user = User(**user_data.model_dump(), role=UserRole.admin)
    user.password = auth.hash_password(user.password)
    await add_item(session, user)
    return {"id": user.id}

@app.post("/api/v1/login/", response_model=str, tags=["auth"])
async def login_user(user_data: BaseUser, session: SessionDependency):
    user_query = select(User).where(User.email == user_data.email)
    user_model = await session.scalar(user_query)
    if user_model is None:
        raise fastapi.HTTPException(status_code=401, detail="User not found")
    if not auth.check_password(user_data.password, user_model.password):
        raise fastapi.HTTPException(status_code=401, detail="Incorrect password")
    user_data = {
        "id": user_model.id,
        "role": user_model.role}
    return auth.create_token(user_data)

@app.get("/api/v1/my_profile/", response_model=GetUserDetails, tags=["auth"])
async def get_user(user_info: TokenDependency, session: SessionDependency):
    user_id = user_info.get("id")
    user = await get_item(session, User, user_id)
    return user

@app.patch("/api/v1/my_profile/", response_model=GetUser, tags=["auth"])
async def update_user(user_info: TokenDependency, user_data: UpdateUser, session: SessionDependency):
    user_id = user_info.get("id")
    user = await get_item(session, User, user_id)
    for field, value in user_data.model_dump(exclude_unset=True).items():
        if field == "password":
            value = auth.hash_password(value)
        setattr(user, field, value)
    user = await add_item(session, user)
    return user

@app.delete("/api/v1/my_profile/", response_model=StatusResponse, tags=["auth"])
async def delete_user(user_info: TokenDependency, session: SessionDependency):
    user_id = user_info.get("id")
    user = await get_item(session, User, user_id)
    if user.books:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete user with books, you should return books first"
        )
    await session.delete(user)
    await session.commit()
    return {"status": "deleted"}

# Users

@app.get("/api/v1/users/", response_model=list[GetUser], tags=["users"])
async def get_users(session: SessionDependency, user: UserAdminDependency):
    query = select(User)
    result = await session.execute(query)
    users = result.unique().scalars().all()
    return users

@app.get("/api/v1/users/{user_id}", response_model=GetUserDetails, tags=["users"])
async def get_user(user_id: int, session: SessionDependency, user: UserAdminDependency):
    user = await get_item(session, User, user_id)
    return user

# Authors

@app.get("/api/v1/authors/", response_model=list[AuthorSchema], tags=["authors"])
async def get_authors(session: SessionDependency):
    query = select(Author)
    result = await session.execute(query)
    authors = result.scalars().all()
    return authors

@app.get("/api/v1/authors/{author_id}", response_model=AuthorSchema, tags=["authors"])
async def get_author(author_id: int, session: SessionDependency):
    author = await get_item(session, Author, author_id)
    return author.dict

@app.post("/api/v1/authors/", response_model=AuthorSchema, tags=["authors"])
async def create_author(
    author: CreateAuthor, session: SessionDependency, user: UserAdminDependency
):
    author = Author(**author.model_dump())
    await add_item(session, author)
    return author

@app.patch("/api/v1/authors/{author_id}", response_model=StatusResponse, tags=["authors"])
async def update_author(
    author_id: int,
    author: UpdateAuthor,
    session: SessionDependency,
    user: UserAdminDependency
):
    db_author = await get_item(session, Author, author_id)
    for field, value in author.model_dump(exclude_unset=True).items():
        setattr(db_author, field, value)
    author = await add_item(session, db_author)
    return {"status": "ok"}

@app.delete("/api/v1/authors/{author_id}", response_model=StatusResponse, tags=["authors"])
async def delete_author(
    author_id: int, session: SessionDependency, user: UserAdminDependency
):
    author = await get_item(session, Author, author_id)
    await session.delete(author)
    await session.commit()
    return {"status": "deleted"}

# Genres

@app.get("/api/v1/genres/", response_model=list[GenreSchema], tags=["genres"])
async def get_genres(session: SessionDependency):
    query = select(Genre)
    result = await session.execute(query)
    genres = result.scalars().all()
    return genres

@app.post("/api/v1/genres/", response_model=GenreSchema, tags=["genres"])
async def create_genre(
    genre: GenreSchema, session: SessionDependency, user: UserAdminDependency
):
    genre = Genre(**genre.model_dump())
    await add_item(session, genre)
    return genre

# Books

@app.get("/api/v1/books/", response_model=list[GetBook], tags=["books"])
async def get_books(query: FiltersDependency, session: SessionDependency):
    return query

@app.get("/api/v1/books/{book_id}", response_model=GetBook, tags=["books"])
async def get_book(book_id: int, session: SessionDependency):
    book = await get_item(session, Book, book_id)
    return book.dict

@app.post("/api/v1/books/", response_model=GetBook, tags=["books"])
async def create_book(
    book: AddBook, session: SessionDependency, user: UserAdminDependency
):
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

# Actions with books

@app.post("/api/v1/books/{book_id}/users/{user_id}", response_model=StatusResponse, tags=["rent actions"])
async def rent_book(
    book_id: int, user_id: int, session: SessionDependency, user: UserAdminDependency
):
    book = await get_item(session, Book, book_id)
    user = await get_item(session, User, user_id)
    if book.available_stock == 0:
        return {"status": "book not available"}
    if len(user.books) == 5:
        raise HTTPException(status_code=400, detail=f"User {user.name} has already 5 books")
    book.available_stock -= 1
    user.books.append(book)
    await session.commit()
    return {"status": "ok"}

@app.delete("/api/v1/books/{book_id}/users/{user_id}", response_model=StatusResponse, tags=["rent actions"])
async def return_book(
    book_id: int, user_id: int, session: SessionDependency, user: UserAdminDependency
):
    book = await get_item(session, Book, book_id)
    user = await get_item(session, User, user_id)
    if book not in user.books:
        raise HTTPException(status_code=404, detail=f"Book {book.title} not found in user's books")
    book.available_stock += 1
    user.books.remove(book)
    await session.commit()
    return {"status": "ok"}
