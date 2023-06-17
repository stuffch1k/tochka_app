
from fastapi import APIRouter, Depends, UploadFile, HTTPException, status, File
import boto3
# import magic

from datetime import datetime

from src.config import REGION_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BUCKETNAME
from sqlalchemy import insert, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse
from .schemas import VideoUpdate, VideoCreate, VideoDelete
from .models import video
from src.database import get_async_session

from src.auth.models import User

from src.auth.router import current_user

router = APIRouter(
    prefix="/video",
    tags=["Video"]
)

session = boto3.session.Session()
s3 = boto3.resource("s3",
                    endpoint_url='https://storage.yandexcloud.net',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
bucket = s3.Bucket(BUCKETNAME)
s4 = session.client("s3",
                    endpoint_url='https://storage.yandexcloud.net',
                    region_name=REGION_NAME,
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

@router.get("/all")
async def get_all_videos(a_session: AsyncSession = Depends(get_async_session)):
    query = select(video)
    res = await a_session.execute(query)
    result = res.all()
    arr=[]
    for row in result:
        arr.append({'id':row.id, 'title':row.title, 'description':row.description, 'posted_at':row.posted_at})
    return arr

# create

@router.post("/upload")
async def upload_video(title: str, description: str, user_id: int,
                        file: UploadFile = File(...),  a_session: AsyncSession = Depends(get_async_session) ):
    KB = 1024
    MB = 1024 * KB
    # print(**new_video.dict())
    supported_types = {'video/mp4': "mp4", 'video/x-matroska': "mkv",
                       'video/ogg': "ogg", 'video/quicktime': "mov", 'video/x-ms-wmv': "wmv",
                       'video/webm': "webm"}
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not found"
        )
    contents = await file.read()
    file_size =  len(contents)
    if not 0 < file_size < 15 * MB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is too longer"
        )
    # file_type = magic.from_buffer(buffer=contents, mime=True)
    if file.content_type not in supported_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not a video"
        )
    key = file.filename
    print(key)
    try:
        bucket.put_object(Body=contents, Key=key)
        stmt = insert(video).values(title=title, url=key, description=description, posted_at=datetime.utcnow(),
                                        user_id=user_id)
        await a_session.execute(stmt)
        await a_session.commit()
        
        return "File was uploaded"
    except:
        return user_id
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID must be uniq",
            
        )
# read
@router.get("/watch")
async def watch_video(video_id: int, a_session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(video).where(video.c.id == video_id)
        res = await a_session.execute(query)
        result = res.first()
        # watch_count=result[6] + 1
        # stmt = update(video).where(video.c.id == video_id).values(watches_count = watch_count)
        # await a_session.execute(stmt)
        # await a_session.commit()
        key = result[2]
        response = s4.get_object(Bucket=BUCKETNAME, Key=key)
        return StreamingResponse(content=response["Body"].iter_chunks(), media_type="video/mp4")
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video with your id doesn't exist"
        )

@router.get("/watch_video")
async def watch_video_front(video_id: int, a_session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(video).where(video.c.id == video_id)
        res = await a_session.execute(query)
        result = res.first()
        # watch_count=result[6] + 1
        # stmt = update(video).where(video.c.id == video_id).values(watches_count = watch_count)
        # await a_session.execute(stmt)
        # await a_session.commit()
        key = result[2]
        response = s4.get_object(Bucket=BUCKETNAME, Key=key)
        return {"id":video_id, "url":f'https://storage.yandexcloud.net/{BUCKETNAME}/{key}'}
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video with your id doesn't exist"
        )


# update
@router.patch("/edit")
async def edit_video(video_up:VideoUpdate, user: User = Depends(current_user), a_session: AsyncSession = Depends(get_async_session)):
    query = select(video).where(video.c.id==video_up.id)
    res = await a_session.execute(query)
    result = res.first()
    if result is None:
        return f"Video {video_up.id} doesn't exist"
    elif result.user_id != user.id:
        return f"You are not author of the video"
    else:
        stmt = update(video).where(video.c.id==video_up.id).values(**video_up.dict())
        await a_session.execute(stmt)
        await a_session.commit()
        return f"Video was updated"
    # st= **video_up.dict()
    # try:
    #     query = select(video).where(video.c.id == video_id)
    #     res = await a_session.execute(query)
    #     if res.first().user_id == user.id:
    #         stmt = (delete(video).where(video.c.id == video_id))
    #         await a_session.execute(stmt)
    #         await a_session.commit()
    #         return f"Video {video_id} was deleted"
    #     else:
    #         return f"You are not a {user.username}"
    # except:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Inputed incorrected video_id"
    #     )

# delete

# удалять видео из бакета тоже!!
@router.delete("/delete")
async def delete_video(video_id: VideoDelete, user: User = Depends(current_user), a_session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(video).where(video.c.id == video_id.id)
        res = await a_session.execute(query)
        result = res.first()
        if result.user_id == user.id:
            stmt = (delete(video).where(video.c.id == video_id.id))
            s4.delete_object(Bucket=BUCKETNAME, Key=result.url)
            await a_session.execute(stmt)
            await a_session.commit()
            return f"Video {video_id.id} was deleted"
        else:
            return f"You are not author of the video"
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inputed incorrected video_id"
        )
