import fastapi
from fastapi import HTTPException

from lifespan import lifespan
from schema import AuthorSchema, UpdateAuthor, ItemId, StatusResponse
from dependencies import SessionDependency
from models import Author
from crud import get_item, add_item


app = fastapi.FastAPI(
    title = "Library RESTful API",
    version = "0.0.1",
    description = "A RESTful API for managing libraries",
    lifespan = lifespan
)


@app.get("/api/v1/authors/", response_model=list[AuthorSchema], tags=["authors"])
async def get_authors(session: SessionDependency):
    return []

@app.get("/api/v1/authors/{author_id}", response_model=AuthorSchema, tags=["authors"])
async def get_author(author_id: int, session: SessionDependency):
    author = await get_item(session, Author, author_id)
    return author.dict

@app.post("/api/v1/authors/", response_model=AuthorSchema, tags=["authors"])
async def create_author(author: AuthorSchema, session: SessionDependency):
    author = Author(**author.dict())
    await add_item(session, author)
    return author

@app.patch("/api/v1/authors/{author_id}", response_model=StatusResponse, tags=["authors"])
async def update_author(
    author_id: int,
    author: UpdateAuthor,
    session: SessionDependency
):
    db_author = await get_item(session, Author, author_id)
    for field, value in author.dict(exclude_unset=True).items():
        setattr(db_author, field, value)
    author = await add_item(session, db_author)
    return {"status": "ok"}

@app.delete("/api/v1/authors/{author_id}", response_model=StatusResponse, tags=["authors"])
async def delete_author(author_id: int, session: SessionDependency):
    author = await get_item(session, Author, author_id)
    await session.delete(author)
    await session.commit()
    return {"status": "deleted"}