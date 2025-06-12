from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
import uuid
from typing import Optional
import io
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status
from sqlalchemy.sql import text
import logging
from fastapi.exceptions import RequestValidationError
import json

from . import crud, models, schemas
from .database import SessionLocal, engine

# Configure a basic logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the database tables
models.Base.metadata.create_all(bind=engine)

# Create the FastAPI app instance
app = FastAPI(
    title="Burn After Reading",
    description="A secure, private way to share self-destructing messages and files.",
    version="0.2.0",
    expose_headers=["Content-Disposition", "Content-Length"],
)

# Create an API router with the /api prefix
api_router = APIRouter(prefix="/api")

# CORS (Cross-Origin Resource Sharing) Configuration
# Default development origins
default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001", 
    "http://localhost:3002",
    "http://127.0.0.1:3002",
]

# Get CORS origins from environment variable or use defaults
cors_origins_env = os.environ.get("CORS_ORIGINS")
if cors_origins_env:
    # Parse comma-separated origins from environment
    origins = [origin.strip() for origin in cors_origins_env.split(",")]
else:
    origins = default_origins.copy()

# Add legacy FRONTEND_URL for backward compatibility  
prod_origin = os.environ.get("FRONTEND_URL")
if prod_origin and prod_origin not in origins:
    origins.append(prod_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "Content-Length"],
)

# Custom exception handler for validation errors to get detailed logs
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    # Log the detailed validation errors
    logger.error(f"Caught RequestValidationError: {json.dumps(exc.errors(), indent=2)}")
    # Return the default 422 response
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@api_router.post("/create", response_model=schemas.NoteResponse)
def create_text_note(note: schemas.NoteCreate, db: Session = Depends(get_db)):
    """
    创建文本笔记
    """
    if not note.content:
        raise HTTPException(status_code=400, detail="Content is required for text notes")
    
    db_note = crud.create_text_note(db, note=note)

    # Manually set the has_password attribute before returning.
    # This is required by the NoteResponse schema.
    db_note.has_password = db_note.password_hash is not None

    # Construct the full URL for the note
    # This should be handled by the frontend, but we provide it for convenience.
    # In a real app, the base URL should come from a config file.

    return db_note

@api_router.post("/upload", response_model=schemas.NoteResponse)
async def upload_file(
    file: UploadFile = File(...),
    password: Optional[str] = Form(None),
    expiration_type: str = Form("read_once"),  # Receive as a raw string
    db: Session = Depends(get_db)
):
    """
    上传文件笔记 (最大5MB)
    """
    # Manually validate and convert the string to the Enum
    try:
        expiration_enum = models.ExpirationType(expiration_type)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid expiration type '{expiration_type}'. Valid options are: {[e.value for e in models.ExpirationType]}"
        )

    file_data = await file.read()
    
    file_note_create = schemas.FileNoteCreate(
        password=password,
        expiration_type=expiration_enum  # Use the validated enum
    )
    
    filename_str = file.filename if file.filename is not None else "file"

    db_note = crud.create_file_note(
        db=db,
        file_data=file_data,
        filename=filename_str,
        content_type=file.content_type or "application/octet-stream",
        file_note=file_note_create
    )

    # Manually set the has_password attribute before returning.
    db_note.has_password = db_note.password_hash is not None

    return db_note

@api_router.get("/note/{note_id}/info", response_model=schemas.NoteResponse)
def get_note_info(note_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    获取笔记信息（不删除，用于前端确认是否需要密码）
    """
    note = crud.get_note_info(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found or expired")
    
    # Manually set the has_password attribute before returning.
    note.has_password = note.password_hash is not None
    
    return note

@api_router.post("/note/{note_id}")
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

@api_router.post("/note/{note_id}/download")
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
@api_router.get("/note/{note_id}")
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

@api_router.post("/cleanup")
def cleanup_expired(db: Session = Depends(get_db)):
    """
    手动清理过期笔记（管理员端点）
    """
    count = crud.cleanup_expired_notes(db)
    return {"message": f"Cleaned up {count} expired notes"}

# Define a health check endpoint at the root level for the entire service
@api_router.get("/health", status_code=status.HTTP_200_OK, tags=["Service Health"])
async def health_check():
    """
    Checks if the service is running and can connect to the database.
    This endpoint is used for health checks by Docker and other services.
    It's at the root path, so docker-compose healthcheck will be http://.../health
    """
    try:
        # Check database connectivity
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            return {"status": "ok", "database": "connected"}
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Health check failed: Database connection error - {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        )

# Include the API router in the main app
app.include_router(api_router) 