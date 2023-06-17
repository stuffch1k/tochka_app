from fastapi import APIRouter, Depends, UploadFile, HTTPException, status, File
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_session

from .models import like
from src.auth.router import current_user
from src.auth.models import User
from sqlalchemy import insert, select, delete, update, and_

router = APIRouter(
    prefix="/like",
    tags=["Like"]
)


@router.get("/video")
async def video_like_count(video_id: int, a_session: AsyncSession = Depends(get_async_session)):
    query = select(like).where(like.c.video_id == video_id)
    res = await a_session.execute(query)
    result = res.all()
    return len(result)


@router.get("/liked_videos")
async def user_like_count(user: User = Depends(current_user), a_session: AsyncSession = Depends(get_async_session)):
    query = select(like).where(like.c.user_id == user.id)
    res = await a_session.execute(query)
    result = res.all()
    if len(result) == 0:
        return "You didn't like any video"
    arr = []
    for row in result:
        arr.append({"video_id": row.video_id})
    return arr


@router.post("")
async def like_dislike(video_id: int, user_id: int,
                       a_session: AsyncSession = Depends(get_async_session)):
    query = select(like).where(and_(like.c.video_id == video_id, like.c.user_id == user_id))
    res = await a_session.execute(query)
    result = res.first()
    if result is None:
        try:
            stmt = insert(like).values(video_id=video_id, user_id=user_id)
            await a_session.execute(stmt)
            await a_session.commit()
            return "You liked the video"
        except:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Video doesn't exist"
            )
    else:
        stmt = delete(like).where(and_(like.c.user_id == user_id, like.c.video_id == video_id))
        await a_session.execute(stmt)
        await a_session.commit()
        return "You don't like the video anymore"
