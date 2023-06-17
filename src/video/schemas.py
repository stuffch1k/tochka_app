from datetime import datetime

from pydantic import BaseModel

class VideoCreate(BaseModel):
    id: int
    title: str
    # url: str
    description: str
    date: datetime
    user_id: int

class VideoUpdate(BaseModel):
    id: int
    title: str
    description: str

class VideoDelete(BaseModel):
    id: int