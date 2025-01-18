from typing import Annotated, Any, Dict, Optional
from fastapi import Depends, HTTPException, Query
from sqlalchemy import select

from models import Session, UserRole, User, Book, Author, Genre
from auth import get_current_user


async def get_session():
    async with Session() as session:
        return session

SessionDependency = Annotated[Session, Depends(get_session, use_cache=True)]

def require_role(role: UserRole):
    def role_dependency(current_user_data: dict = Depends(get_current_user)):
        if current_user_data.get("role") != role:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required role: {role}"
            )
        return current_user_data
    return role_dependency

UserAdminDependency = Annotated[User, Depends(require_role(UserRole.admin))]

TokenDependency = Annotated[dict, Depends(get_current_user)]

async def get_filters(
    session: SessionDependency,
    title: Optional[str] = Query(default=None, description="Поиск по заголовку"),
    release_year: Optional[int] = Query(default=None, description="Поиск по году выпуска"),
    author: Optional[str] = Query(default=None, description="Поиск по авторам"),
    genre: Optional[str] = Query(default=None, description="Поиск по жанрам")
) -> Dict[str, Any]:
    query = select(Book).where(Book.available_stock > 0)
    if title is not None:
        query = query.where(Book.title.icontains(title))
    if release_year is not None:
        query = query.where(Book.release_year == release_year)
    if author is not None:
        query = query.join(Book.authors).filter(Author.name.icontains(author))
    if genre is not None:
        query = query.join(Book.genres).filter(Genre.name.icontains(genre))
    result = await session.execute(query)
    books = result.unique().scalars().all()
    return books

FiltersDependency = Annotated[Dict[str, Any], Depends(get_filters)]
