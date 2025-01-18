from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from models import Session, Author, ORM_OBJECT, ORM_CLS


async def add_item(session: Session, item: ORM_OBJECT) -> ORM_OBJECT:
    session.add(item)
    try:
        await session.commit()
    except IntegrityError as err:
        if err.orig.pgcode == '23505':
            raise HTTPException(
                status_code=409,
                detail='Item already exists'
            )
        raise err
    return item
    
async def get_item(session: Session, cls: ORM_CLS, item_id: int) -> ORM_OBJECT:
    orm_obj = await session.get(cls, item_id)
    if orm_obj is None:
        raise HTTPException(
            status_code=404,
            detail=f'{cls.__name__} not found'
        )
    return orm_obj
