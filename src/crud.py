from sqlalchemy.orm import Session
from fastapi import HTTPException
import uuid
from typing import Optional

from . import models, schemas
from .utils import hash_password, verify_password, calculate_expiration_time, is_note_expired, format_file_size

def get_note_and_delete(db: Session, note_id: uuid.UUID, password: Optional[str] = None):
    """
    获取笔记并立即删除（阅后即焚）
    支持密码验证和过期检查
    """
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    
    if not note:
        return None
    
    # 检查时间过期
    if note.expires_at and is_note_expired(note.expires_at):
        db.delete(note)
        db.commit()
        return None
    
    # 检查密码保护
    if note.password_hash:
        if not password:
            raise HTTPException(status_code=401, detail="Password required")
        if not verify_password(password, note.password_hash):
            raise HTTPException(status_code=401, detail="Invalid password")
    
    # FIX: Only delete the note if its expiration type is 'READ_ONCE'.
    # Time-based notes should persist until their expiration time.
    if note.expiration_type == models.ExpirationType.READ_ONCE:
        db.delete(note)
        db.commit()
    
    return note

def create_text_note(db: Session, note: schemas.NoteCreate):
    """
    创建文本笔记
    """
    # 处理密码
    password_hash = None
    if note.password:
        password_hash = hash_password(note.password)
    
    # 计算过期时间
    expires_at = calculate_expiration_time(note.expiration_type)
    
    db_note = models.Note(
        content=note.content,
        password_hash=password_hash,
        expiration_type=note.expiration_type,
        expires_at=expires_at
    )
    
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def create_file_note(db: Session, file_data: bytes, filename: str, content_type: str, 
                    file_note: schemas.FileNoteCreate):
    """
    创建文件笔记
    """
    # 检查文件大小限制 (5MB)
    if len(file_data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 5MB.")
    
    # 处理密码
    password_hash = None
    if file_note.password:
        password_hash = hash_password(file_note.password)
    
    # 计算过期时间
    expires_at = calculate_expiration_time(file_note.expiration_type)
    
    db_note = models.Note(
        filename=filename,
        file_data=file_data,
        content_type=content_type,
        file_size=format_file_size(len(file_data)),
        password_hash=password_hash,
        expiration_type=file_note.expiration_type,
        expires_at=expires_at
    )
    
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def get_note_info(db: Session, note_id: uuid.UUID):
    """
    获取笔记基本信息（不删除，用于确认是否需要密码）
    """
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    
    if not note:
        return None
    
    # 检查时间过期
    if note.expires_at and is_note_expired(note.expires_at):
        db.delete(note)
        db.commit()
        return None
    
    return note

def cleanup_expired_notes(db: Session):
    """
    清理所有已过期的笔记（定期维护任务）
    """
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    
    expired_notes = db.query(models.Note).filter(
        models.Note.expires_at.isnot(None),
        models.Note.expires_at < now
    ).all()
    
    count = len(expired_notes)
    for note in expired_notes:
        db.delete(note)
    
    db.commit()
    return count 