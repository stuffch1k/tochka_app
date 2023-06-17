
from pydantic import BaseModel

class CommentCreate(BaseModel):
    video_id: int
    comment: str

class CommentDelete(BaseModel):
    video_id: int
