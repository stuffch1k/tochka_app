from datetime import datetime

from sqlalchemy import Table, Column, Integer, TEXT, TIMESTAMP, ForeignKey, MetaData
from sqlalchemy.orm import relationship

# from src.auth.models import user
# from src.video.models import video

from src.user.models import s_user
from src.video.models import video

metadata = MetaData()
comment = Table(
    "comment",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("text", TEXT, nullable=False),
    Column("video_id", Integer, ForeignKey(video.c.id), nullable=False, default=1),
    Column("user_id", Integer, ForeignKey(s_user.c.id), nullable=False, default=1),
    Column("posted_at", TIMESTAMP, default=datetime.utcnow)
)