import datetime
from pydantic import BaseModel
from typing import Optional, Dict, Any

class DocumentMetadata(BaseModel):
    document_name: str
    vendor: str
    solution_category: str
    page_number: Optional[int] = 1
    created_date: Optional[str] = None

class DocumentResponse(BaseModel):
    id: int
    document_name: str
    file_path: str
    file_type: str
    vendor: str
    solution_category: str
    page_count: int
    chunk_count: int
    file_size_bytes: int
    status: str
    doc_metadata: Dict[str, Any] = {}
    created_date: datetime.datetime

    class Config:
        from_attributes = True

class DocumentUploadResponse(BaseModel):
    message: str
    document: DocumentResponse
