from datetime import datetime
from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, TEXT, Boolean, MetaData


metadata = MetaData()
s_user = Table(
    "s_user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, nullable=False),
    Column("email", String, nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("is_active", Boolean, default= False),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow)
)