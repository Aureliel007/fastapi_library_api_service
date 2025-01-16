import fastapi

from .lifespan import lifespan
from .schema import *


app = fastapi.FastAPI(
    title = "Library RESTful API",
    version = "0.0.1",
    description = "A RESTful API for managing libraries",
    lifespan = lifespan
)


@app.get("api/v1/authors/", response_model=list[Author])
async def get_authors():
    return []

@app.get("api/v1/authors/{author_id}", response_model=Author)
async def get_author(author_id: int):
    return {}

@app.post("api/v1/authors/", response_model=Author)
async def create_author(author: Author):
    return {}

@app.patch("api/v1/authors/{author_id}", response_model=Author)
async def update_author(author_id: int, author: UpdateAuthor):
    return {}

@app.delete("api/v1/authors/{author_id}", response_model=StatusResponse)
async def delete_author(author_id: int):
    return {"status": "deleted"}