import uuid
import datetime
from typing import Optional
from pydantic import BaseModel, Field
from .models import ExpirationType

# Pydantic models (schemas) for data validation and serialization.

class NoteBase(BaseModel):
    content: Optional[str] = None
    password: Optional[str] = Field(None, description="Optional password to protect the note")
    expiration_type: ExpirationType = Field(ExpirationType.READ_ONCE, description="When should the note expire")

class NoteCreate(NoteBase):
    pass

class FileNoteCreate(BaseModel):
    password: Optional[str] = Field(None, description="Optional password to protect the file")
    expiration_type: ExpirationType = Field(ExpirationType.READ_ONCE, description="When should the file expire")

class NoteResponse(BaseModel):
    model_config = {"from_attributes": True}
    
    id: uuid.UUID
    content: Optional[str] = None
    filename: Optional[str] = None
    content_type: Optional[str] = None
    file_size: Optional[str] = None
    has_password: bool = Field(description="Whether this note is password protected")
    expiration_type: ExpirationType
    expires_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime

class NoteAccess(BaseModel):
    password: Optional[str] = Field(None, description="Password if the note is protected")

class FileDownload(BaseModel):
    filename: str
    content_type: str
    file_size: str 