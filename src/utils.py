import bcrypt
import datetime
from typing import Optional
from .models import ExpirationType

def hash_password(password: str) -> str:
    """
    使用bcrypt对密码进行哈希处理
    """
    # 生成salt并哈希密码
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """
    验证密码是否匹配哈希值
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def calculate_expiration_time(expiration_type: ExpirationType) -> Optional[datetime.datetime]:
    """
    根据过期类型计算具体的过期时间
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    
    if expiration_type == ExpirationType.READ_ONCE:
        return None  # 阅读后立即删除，不设置时间过期
    elif expiration_type == ExpirationType.HOURS_1:
        return now + datetime.timedelta(hours=1)
    elif expiration_type == ExpirationType.HOURS_24:
        return now + datetime.timedelta(hours=24)
    elif expiration_type == ExpirationType.DAYS_7:
        return now + datetime.timedelta(days=7)
    else:
        return None

def is_note_expired(expires_at: Optional[datetime.datetime]) -> bool:
    """
    检查笔记是否已过期
    """
    if expires_at is None:
        return False  # 没有设置过期时间，不过期
    
    now = datetime.datetime.now(datetime.timezone.utc)
    
    # 如果expires_at没有时区信息，假设它是UTC时间
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=datetime.timezone.utc)
    
    return now > expires_at

def format_file_size(size_bytes: int) -> str:
    """
    将文件大小格式化为易读的字符串
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB" 