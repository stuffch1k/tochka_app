from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, Text
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_session
from src.auth.router import current_user
from src.auth.models import User
from sqlalchemy import insert, select, delete, update, and_
from .models import comment
from .schemas import CommentCreate, CommentDelete
from datetime import datetime

router = APIRouter(
    prefix="/comment",
    tags=["Comment"]
)


# watch all comments of user number
@router.get("/all")
async def get_all_user_comments(a_session: AsyncSession = Depends(get_async_session),
                                user: User = Depends(current_user)):
    query = select(comment).where(comment.c.user_id == user.id)
    res = await a_session.execute(query)
    result = res.all()
    if len(result) == 0:
        return f"You have not comments"
    arr = []
    for row in result:
        arr.append({'id': row.id, 'text': row.text, 'video_id': row.video_id, 'posted_at': row.posted_at})
    return arr


@router.get("/video")
async def get_all_video_comments(video_id: int, a_session: AsyncSession = Depends(get_async_session)):
    query = select(comment).where(comment.c.video_id == video_id)
    res = await a_session.execute(query)
    result = res.all()
    if len(result) == 0:
        return f"Video doesn't exist"
    arr = []
    for row in result:
        arr.append({'id': row.id, 'text': row.text, 'user_id': row.user_id, 'posted_at': row.posted_at})
    return arr


# read proc for one comment??

# тут лучше использовать схему
@router.post("")
async def create_comment(c_text: CommentCreate, user: User = Depends(current_user),
                         a_session: AsyncSession = Depends(get_async_session)):
    if c_text.comment == "":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Comment can't be empty"
        )

    try:
        stmt = insert(comment).values(video_id=c_text.video_id, text=c_text.comment, posted_at=datetime.utcnow(),
                                      user_id=user.id)

        await a_session.execute(stmt)
        await a_session.commit()
        return {"status": "OK"}
    except:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Video doesn't exist"
        )


# и тут тоже
@router.patch("")
async def edit_comment(c_text: CommentCreate, user: User = Depends(current_user),
                       a_session: AsyncSession = Depends(get_async_session)):
    query = select(comment).where(and_(comment.c.video_id == c_text.video_id, comment.c.user_id == user.id))
    res = await a_session.execute(query)
    result = res.first()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Incorrect input"
        )
    else:
        stmt = update(comment).where(and_(comment.c.video_id == c_text.video_id, comment.c.user_id == user.id)).values(
            text=c_text.comment)
        await a_session.execute(stmt)
        await a_session.commit()
        return f"Comment was updated"


@router.delete("")
async def delete_comment(c_text: CommentDelete, user: User = Depends(current_user),
                         a_session: AsyncSession = Depends(get_async_session)):
    query = select(comment).where(and_(comment.c.video_id == c_text.video_id, comment.c.user_id == user.id))
    res = await a_session.execute(query)
    result = res.first()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Incorrect input"
        )
    else:
        stmt = delete(comment).where(and_(comment.c.video_id == c_text.video_id, comment.c.user_id == user.id))
        await a_session.execute(stmt)
        await a_session.commit()
        return f"Comment was deleted"
