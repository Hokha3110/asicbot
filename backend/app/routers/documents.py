import os
import shutil
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services.doc_parser import DocumentParserService
from app.services.vector_service import vector_service
from app.services.gdrive_service import gdrive_service
from app.utils.security import require_current_user, get_admin_user

router = APIRouter(prefix="/api/v1/documents", tags=["Document Center"])

@router.get("", response_model=List[DocumentResponse])
def list_documents(
    vendor: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Document)
    if vendor:
        query = query.filter(Document.vendor.ilike(f"%{vendor}%"))
    if category:
        query = query.filter(Document.solution_category.ilike(f"%{category}%"))
    return query.order_by(Document.created_date.desc()).all()

@router.get("/gdrive-status")
def get_gdrive_status():
    """
    Returns Google Drive Cloud storage sync status.
    """
    return {
        "enabled": settings.GOOGLE_DRIVE_ENABLED,
        "is_connected": gdrive_service.is_configured(),
        "folder_id": settings.GOOGLE_DRIVE_FOLDER_ID or "Chưa cấu hình Folder ID",
        "storage_mode": "Hybrid (Linux Server + Google Drive Cloud)",
        "last_sync_time": gdrive_service.last_sync_time
    }

@router.post("/test-gdrive")
def test_gdrive_connection(
    payload: Optional[Dict[str, Any]] = Body(None),
    current_user: User = Depends(require_current_user)
):
    """
    Tests credentials and folder access for Google Drive.
    """
    folder_id = payload.get("folder_id") if payload else None
    sa_json = payload.get("service_account_json") if payload else None
    return gdrive_service.test_connection(folder_id=folder_id, sa_json=sa_json)

@router.post("/sync-gdrive")
def sync_documents_from_gdrive(
    payload: Optional[Dict[str, Any]] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user)
):
    """
    Pulls and indexes all solution documents from Google Drive into Linux server & Vector DB.
    """
    folder_id = payload.get("folder_id") if payload else None
    sa_json = payload.get("service_account_json") if payload else None
    result = gdrive_service.sync_all_from_drive(db, folder_id=folder_id, sa_json=sa_json)
    return result

@router.get("/download/{doc_id}")
def download_document(
    doc_id: int,
    db: Session = Depends(get_db)
):
    """
    Downloads document file directly from local Linux server.
    """
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc or not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="File không tồn tại trên máy chủ")

    media_type = "application/pdf" if doc.file_type == "pdf" else "application/octet-stream"
    return FileResponse(
        path=doc.file_path,
        filename=doc.document_name,
        media_type=media_type
    )

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    vendor: Optional[str] = Form(None),
    solution_category: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user)
):
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower().replace(".", "")
    if ext not in ["pdf", "docx", "pptx", "txt"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Định dạng file không hỗ trợ. Vui lòng upload PDF, DOCX hoặc PPTX."
        )

    # 1. Save file locally on Linux server
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    saved_file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    with open(saved_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(saved_file_path)

    # 2. Upload simultaneously to Google Drive Cloud Storage
    mime_type = "application/pdf" if ext == "pdf" else "application/octet-stream"
    gdrive_result = gdrive_service.upload_file_to_drive(saved_file_path, filename, mime_type)

    # 3. Parse text based on format
    if ext == "pdf":
        pages = DocumentParserService.parse_pdf(saved_file_path)
    elif ext == "docx":
        pages = DocumentParserService.parse_docx(saved_file_path)
    elif ext == "pptx":
        pages = DocumentParserService.parse_pptx(saved_file_path)
    else:
        pages = DocumentParserService._fallback_text_extract(saved_file_path)

    # Auto detect vendor/category if not provided
    sample_text = " ".join([p["text"] for p in pages[:3]])
    detected_vendor, detected_cat = DocumentParserService.detect_vendor_and_category(sample_text, filename)
    
    final_vendor = vendor.strip() if (vendor and vendor.strip()) else detected_vendor
    final_category = solution_category.strip() if (solution_category and solution_category.strip()) else detected_cat

    # 4. Chunk document with metadata
    chunks = DocumentParserService.chunk_document(
        pages_content=pages,
        doc_name=filename,
        vendor=final_vendor,
        category=final_category
    )

    # 5. Add to ChromaDB Vector DB
    vector_service.add_chunks(chunks)

    # 6. Save metadata to Database (Tracking both Linux path & Google Drive link)
    doc_metadata = {
        "uploader": current_user.username if current_user else "presales_user",
        "storage": "hybrid_linux_and_gdrive",
        "gdrive_url": gdrive_result.get("drive_url") if gdrive_result else None,
        "gdrive_file_id": gdrive_result.get("file_id") if gdrive_result else None
    }

    doc_record = db.query(Document).filter(Document.document_name == filename).first()
    if not doc_record:
        doc_record = Document(
            document_name=filename,
            file_path=saved_file_path,
            file_type=ext,
            vendor=final_vendor,
            solution_category=final_category,
            page_count=len(pages) or 1,
            chunk_count=len(chunks),
            file_size_bytes=file_size,
            status="indexed",
            doc_metadata=doc_metadata
        )
        db.add(doc_record)
    else:
        doc_record.vendor = final_vendor
        doc_record.solution_category = final_category
        doc_record.page_count = len(pages) or 1
        doc_record.chunk_count = len(chunks)
        doc_record.file_size_bytes = file_size
        doc_record.status = "indexed"
        doc_record.doc_metadata = doc_metadata

    db.commit()
    db.refresh(doc_record)

    return DocumentUploadResponse(
        message=f"Đã lưu tài liệu lên Máy chủ Linux & Google Drive, đồng thời index {len(chunks)} chunks vào Vector Store!",
        document=DocumentResponse.from_orm(doc_record)
    )

@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")
    
    # Remove file from Linux server disk
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    db.delete(doc)
    db.commit()
    return {"message": f"Đã xóa tài liệu '{doc.document_name}' thành công"}
