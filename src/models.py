import uuid
import enum
from sqlalchemy import Column, String, DateTime, LargeBinary, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .database import Base

class ExpirationType(enum.Enum):
    READ_ONCE = "read_once"  # 默认：阅读后立即删除
    HOURS_1 = "hours_1"      # 1小时后删除
    HOURS_24 = "hours_24"    # 24小时后删除
    DAYS_7 = "days_7"        # 7天后删除

class Note(Base):
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 内容字段 - 文本内容或文件名
    content = Column(Text, nullable=True)  # 文本笔记的内容
    
    # 密码保护
    password_hash = Column(String(255), nullable=True)  # bcrypt哈希
    
    # 过期控制
    expiration_type = Column(Enum(ExpirationType), nullable=False, default=ExpirationType.READ_ONCE)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # 具体过期时间
    
    # 文件支持
    filename = Column(String(255), nullable=True)  # 原始文件名
    file_data = Column(LargeBinary, nullable=True)  # 文件内容 (BLOB)
    content_type = Column(String(100), nullable=True)  # MIME类型
    file_size = Column(String(20), nullable=True)  # 文件大小（字节）
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 