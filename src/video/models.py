from datetime import datetime
from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, TEXT, Boolean, MetaData

# from src.auth.models import user
from src.user.models import s_user

metadata = MetaData()
video = Table(
    "video",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
    Column("url", String, nullable=False),
    Column("description", TEXT, nullable=True),
    Column("posted_at", TIMESTAMP, default=datetime.utcnow),
    Column("watches_count", Integer, default=0),
    # Column("likes", Integer, default=0),
    Column("user_id", Integer, ForeignKey(s_user.c.id), default=1),
)

# class Video(Base):
# __tablename__
#     Column("id", Integer, primary_key=True),
#     Column("title", String, nullable=False),
#     Column("url", String, nullable=False),
#     Column("description", String),
#     Column("posted_at", TIMESTAMP, default=datetime.utcnow),
#     Column("user_id", Integer, ForeignKey(user.c.id), default=1),

    # likes = relationship("Like", back_populates="video")
    # comment = relationship("Comment", back_populates="video")
    # watch_history = relationship("WatchHistory", back_populates="video")