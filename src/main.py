from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import uuid
from typing import Optional
import io
import os
from fastapi.middleware.cors import CORSMiddleware

from . import crud, models, schemas
from .database import SessionLocal, engine

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Burn After Reading",
    description="A secure, private way to share self-destructing messages and files.",
    version="0.2.0"
)

# CORS (Cross-Origin Resource Sharing) Configuration
prod_origin = os.environ.get("FRONTEND_URL")
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001", 
    "http://localhost:3002",
    "http://127.0.0.1:3002",
]
if prod_origin:
    origins.append(prod_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "Content-Length"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/create", response_model=schemas.NoteResponse)
def create_text_note(note: schemas.NoteCreate, db: Session = Depends(get_db)):
    """
    创建文本笔记
    """
    if not note.content:
        raise HTTPException(status_code=400, detail="Content is required for text notes")
    
    db_note = crud.create_text_note(db, note)
    
    # 构建响应，不包含密码哈希
    return schemas.NoteResponse(
        id=db_note.id,
        content=db_note.content,
        has_password=bool(db_note.password_hash),
        expiration_type=db_note.expiration_type,
        expires_at=db_note.expires_at,
        created_at=db_note.created_at
    )

@app.post("/upload", response_model=schemas.NoteResponse)
async def upload_file(
    file: UploadFile = File(...),
    password: Optional[str] = Form(None),
    expiration_type: models.ExpirationType = Form(models.ExpirationType.READ_ONCE),
    db: Session = Depends(get_db)
):
    """
    上传文件笔记 (最大5MB)
    """
    # 读取文件内容
    file_data = await file.read()
    
    # 创建文件笔记请求对象
    file_note = schemas.FileNoteCreate(
        password=password,
        expiration_type=expiration_type
    )
    
    db_note = crud.create_file_note(
        db=db,
        file_data=file_data,
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        file_note=file_note
    )
    
    return schemas.NoteResponse(
        id=db_note.id,
        filename=db_note.filename,
        content_type=db_note.content_type,
        file_size=db_note.file_size,
        has_password=bool(db_note.password_hash),
        expiration_type=db_note.expiration_type,
        expires_at=db_note.expires_at,
        created_at=db_note.created_at
    )

@app.get("/note/{note_id}/info", response_model=schemas.NoteResponse)
def get_note_info(note_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    获取笔记信息（不删除，用于前端确认是否需要密码）
    """
    note = crud.get_note_info(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found or expired")
    
    return schemas.NoteResponse(
        id=note.id,
        content=note.content if not note.file_data else None,
        filename=note.filename,
        content_type=note.content_type,
        file_size=note.file_size,
        has_password=bool(note.password_hash),
        expiration_type=note.expiration_type,
        expires_at=note.expires_at,
        created_at=note.created_at
    )

@app.post("/note/{note_id}")
def access_note(note_id: uuid.UUID, note_access: schemas.NoteAccess, db: Session = Depends(get_db)):
    """
    访问文本笔记内容（带密码验证，访问后删除）
    """
    note = crud.get_note_and_delete(db, note_id, note_access.password)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found or expired")
    
    if note.file_data:
        raise HTTPException(status_code=400, detail="This is a file note, use /note/{note_id}/download")
    
    return {"content": note.content, "expiration_type": note.expiration_type.value}

@app.post("/note/{note_id}/download")
def download_file(note_id: uuid.UUID, note_access: schemas.NoteAccess, db: Session = Depends(get_db)):
    """
    下载文件笔记（带密码验证，下载后删除）
    """
    note = crud.get_note_and_delete(db, note_id, note_access.password)
    if not note:
        raise HTTPException(status_code=404, detail="File not found or expired")
    
    if not note.file_data:
        raise HTTPException(status_code=400, detail="This is a text note, use /note/{note_id}")
    
    # 返回文件流
    file_stream = io.BytesIO(note.file_data)
    
    return StreamingResponse(
        file_stream,
        media_type=note.content_type,
        headers={
            "Content-Disposition": f"attachment; filename=\"{note.filename}\"",
            "Content-Length": str(len(note.file_data))
        }
    )

# 保持向后兼容的旧API端点
@app.get("/note/{note_id}")
def get_note_legacy(note_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    旧版本API兼容性端点（无密码保护）
    """
    note = crud.get_note_and_delete(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found or expired")
    
    if note.password_hash:
        raise HTTPException(status_code=401, detail="This note is password protected, use POST /note/{note_id}")
    
    if note.file_data:
        raise HTTPException(status_code=400, detail="This is a file note, use POST /note/{note_id}/download")
    
    return {"content": note.content}

@app.get("/health")
def health_check():
    """
    健康检查端点
    """
    return {"status": "healthy", "version": "0.2.0"}

@app.post("/cleanup")
def cleanup_expired(db: Session = Depends(get_db)):
    """
    手动清理过期笔记（管理员端点）
    """
    count = crud.cleanup_expired_notes(db)
    return {"message": f"Cleaned up {count} expired notes"} 