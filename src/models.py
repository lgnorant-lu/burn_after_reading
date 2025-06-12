import uuid
import datetime
from sqlalchemy import Column, String, DateTime, Text, LargeBinary, Boolean, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from .database import Base
import enum

class ExpirationType(str, enum.Enum):
    READ_ONCE = "read_once"
    ONE_HOUR = "one_hour"
    ONE_DAY = "one_day"
    ONE_WEEK = "one_week"

class Note(Base):
    __tablename__ = "notes"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    expiration_type: Mapped[ExpirationType] = mapped_column(SQLAlchemyEnum(ExpirationType), nullable=False)
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    
    # For file storage
    filename: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    file_data: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    content_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(String, nullable=True)