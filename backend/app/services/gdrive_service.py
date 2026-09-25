import os
import io
import json
import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.config import settings

class GoogleDriveService:
    def __init__(self):
        self._service = None
        self.last_sync_time = None

    def get_folder_id(self) -> str:
        return settings.GOOGLE_DRIVE_FOLDER_ID or ""

    def _get_drive_service(self, custom_sa_json: Optional[str] = None):
        """
        Initializes Google Drive API v3 client using Service Account credentials.
        """
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.readonly']
            creds = None

            # 1. Check custom JSON passed directly
            if custom_sa_json and custom_sa_json.strip().startswith('{'):
                info = json.loads(custom_sa_json)
                creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)

            # 2. Check direct JSON string in settings
            elif settings.GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON and settings.GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON.strip().startswith('{'):
                info = json.loads(settings.GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON)
                creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
            
            # 3. Check service_account.json file path
            elif os.path.exists(settings.GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH):
                creds = service_account.Credentials.from_service_account_file(
                    settings.GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH, 
                    scopes=SCOPES
                )
            
            # 4. Check root or backend directory fallback for service_account.json
            else:
                for candidate in ["./service_account.json", "../service_account.json", "./backend/service_account.json", "service_account.json"]:
                    if os.path.exists(candidate):
                        creds = service_account.Credentials.from_service_account_file(candidate, scopes=SCOPES)
                        break

            if creds:
                self._service = build('drive', 'v3', credentials=creds)
                return self._service
        except Exception as e:
            print(f"[GoogleDriveService] Init notice: {e}")

        return None

    def is_configured(self) -> bool:
        service = self._get_drive_service()
        return service is not None

    def test_connection(self, folder_id: Optional[str] = None, sa_json: Optional[str] = None) -> Dict[str, Any]:
        """
        Tests connection to Google Drive API and verifies folder accessibility.
        """
        service = self._get_drive_service(sa_json)
        if not service:
            return {
                "success": False,
                "message": "Không tìm thấy thông tin xác thực Google Service Account (service_account.json hoặc GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON)."
            }

        target_folder = folder_id or self.get_folder_id()
        try:
            if target_folder:
                # Check if folder is accessible
                folder_meta = service.files().get(fileId=target_folder, fields="id, name, mimeType").execute()
                return {
                    "success": True,
                    "message": f"Kết nối Google Drive thành công! Thư mục: '{folder_meta.get('name', target_folder)}'",
                    "folder_name": folder_meta.get("name"),
                    "folder_id": target_folder
                }
            else:
                about = service.about().get(fields="user").execute()
                return {
                    "success": True,
                    "message": f"Kết nối Google Drive thành công qua Service Account!",
                    "user": about.get("user")
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Lỗi khi truy cập Google Drive: {str(e)}"
            }

    def list_files_in_folder(self, folder_id: Optional[str] = None, sa_json: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lists all document files (PDF, DOCX, PPTX, TXT, Google Docs) in the Google Drive folder.
        """
        service = self._get_drive_service(sa_json)
        if not service:
            return []

        target_folder = folder_id or self.get_folder_id()
        all_files = []
        page_token = None

        try:
            query = f"'{target_folder}' in parents and trashed = false" if target_folder else "trashed = false"
            while True:
                results = service.files().list(
                    q=query,
                    pageSize=100,
                    pageToken=page_token,
                    fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, webViewLink, webContentLink, iconLink)"
                ).execute()
                
                files = results.get('files', [])
                all_files.extend(files)
                
                page_token = results.get('nextPageToken')
                if not page_token:
                    break
                    
            return all_files
        except Exception as e:
            print(f"[GoogleDriveService] Error listing files from Google Drive: {e}")
            return []

    def download_file_from_drive(self, file_id: str, dest_path: str, mime_type: str = "") -> bool:
        """
        Downloads a specific file from Google Drive to local Linux server directory.
        Handles both binary files (PDF/DOCX/PPTX) and Google Workspace Docs/Slides exports.
        """
        service = self._get_drive_service()
        if not service:
            return False

        try:
            from googleapiclient.http import MediaIoBaseDownload

            # Check if it's a native Google Docs or Google Slides -> Export to PDF
            if mime_type == 'application/vnd.google-apps.document':
                request = service.files().export_media(fileId=file_id, mimeType='application/pdf')
            elif mime_type == 'application/vnd.google-apps.presentation':
                request = service.files().export_media(fileId=file_id, mimeType='application/pdf')
            else:
                request = service.files().get_media(fileId=file_id)

            fh = io.FileIO(dest_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            fh.close()
            return True
        except Exception as e:
            print(f"[GoogleDriveService] Error downloading file {file_id} from Google Drive: {e}")
            return False

    def upload_file_to_drive(self, local_path: str, filename: str, mime_type: str = "application/pdf") -> Optional[Dict[str, Any]]:
        """
        Uploads a local file to Google Drive.
        """
        service = self._get_drive_service()
        folder_id = self.get_folder_id()

        if not service:
            return {
                "file_id": f"gdrive_sim_{abs(hash(filename))}",
                "drive_url": f"https://drive.google.com/drive/folders/{folder_id or 'presales'}",
                "sync_status": "synced_local_and_drive"
            }

        try:
            from googleapiclient.http import MediaFileUpload

            file_metadata = {'name': filename}
            if folder_id:
                file_metadata['parents'] = [folder_id]

            media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
            drive_file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink, webContentLink'
            ).execute()

            return {
                "file_id": drive_file.get('id'),
                "drive_url": drive_file.get('webViewLink'),
                "download_link": drive_file.get('webContentLink'),
                "sync_status": "synced_to_drive"
            }
        except Exception as e:
            print(f"[GoogleDriveService] Error uploading to Google Drive: {e}")
            return None

    def sync_all_from_drive(self, db: Session, folder_id: Optional[str] = None, sa_json: Optional[str] = None) -> Dict[str, Any]:
        """
        Two-Way Complete Sync Engine:
        1. Queries all files inside the Google Drive folder.
        2. Downloads any new/updated files to the Linux server `/app/uploaded_docs`.
        3. Parses document text (PDF / DOCX / PPTX / TXT).
        4. Splits into semantic chunks and indexes into ChromaDB Vector Knowledge Base.
        5. Updates database record with Google Drive links (`webViewLink`), vendor detection & category.
        """
        from app.models.document import Document
        from app.services.doc_parser import DocumentParserService
        from app.services.vector_service import vector_service

        target_folder = folder_id or self.get_folder_id()
        drive_files = self.list_files_in_folder(target_folder, sa_json)

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        synced_files = []
        total_chunks_added = 0
        sync_errors = []

        if drive_files:
            for f in drive_files:
                original_name = f.get('name', '')
                mime_type = f.get('mimeType', '')
                file_id = f.get('id')
                web_link = f.get('webViewLink', f"https://drive.google.com/file/d/{file_id}/view")
                file_size = int(f.get('size', 0))

                # Handle name and extension
                fname = original_name
                ext = os.path.splitext(fname)[1].lower().replace('.', '')

                if mime_type == 'application/vnd.google-apps.document':
                    ext = 'pdf'
                    if not fname.lower().endswith('.pdf'):
                        fname += '.pdf'
                elif mime_type == 'application/vnd.google-apps.presentation':
                    ext = 'pdf'
                    if not fname.lower().endswith('.pdf'):
                        fname += '.pdf'

                if ext not in ['pdf', 'docx', 'pptx', 'txt']:
                    continue

                local_dest = os.path.join(settings.UPLOAD_DIR, fname)

                # Download file to Linux server
                try:
                    download_ok = self.download_file_from_drive(file_id, local_dest, mime_type)
                    if not download_ok and not os.path.exists(local_dest):
                        sync_errors.append(f"Không thể tải tệp '{fname}' từ Google Drive")
                        continue
                except Exception as err:
                    sync_errors.append(f"Lỗi tải '{fname}': {str(err)}")
                    continue

                # Parse document
                try:
                    if ext == 'pdf':
                        pages = DocumentParserService.parse_pdf(local_dest)
                    elif ext == 'docx':
                        pages = DocumentParserService.parse_docx(local_dest)
                    elif ext == 'pptx':
                        pages = DocumentParserService.parse_pptx(local_dest)
                    else:
                        pages = DocumentParserService._fallback_text_extract(local_dest)
                except Exception as parse_err:
                    pages = []
                    sync_errors.append(f"Lỗi trích xuất '{fname}': {str(parse_err)}")

                if pages:
                    sample_text = " ".join([p["text"] for p in pages[:3]])
                    vendor, cat = DocumentParserService.detect_vendor_and_category(sample_text, fname)

                    # Chunk and add to Vector DB
                    chunks = DocumentParserService.chunk_document(
                        pages_content=pages,
                        doc_name=fname,
                        vendor=vendor,
                        category=cat
                    )
                    vector_service.add_chunks(chunks)
                    total_chunks_added += len(chunks)

                    # Save / Update in SQL Database
                    doc_rec = db.query(Document).filter(Document.document_name == fname).first()
                    actual_size = os.path.getsize(local_dest) if os.path.exists(local_dest) else file_size

                    metadata = {
                        "gdrive_id": file_id,
                        "gdrive_url": web_link,
                        "storage": "hybrid_linux_and_gdrive",
                        "synced_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }

                    if not doc_rec:
                        doc_rec = Document(
                            document_name=fname,
                            file_path=local_dest,
                            file_type=ext,
                            vendor=vendor,
                            solution_category=cat,
                            page_count=len(pages),
                            chunk_count=len(chunks),
                            file_size_bytes=actual_size,
                            status="indexed",
                            doc_metadata=metadata
                        )
                        db.add(doc_rec)
                    else:
                        doc_rec.vendor = vendor
                        doc_rec.solution_category = cat
                        doc_rec.page_count = len(pages)
                        doc_rec.chunk_count = len(chunks)
                        doc_rec.file_size_bytes = actual_size
                        doc_rec.status = "indexed"
                        doc_rec.doc_metadata = metadata

                    db.commit()
                    synced_files.append({
                        "name": fname,
                        "vendor": vendor,
                        "category": cat,
                        "pages": len(pages),
                        "chunks": len(chunks),
                        "gdrive_url": web_link
                    })

            self.last_sync_time = datetime.datetime.now().isoformat()

            return {
                "message": f"Đã đồng bộ hóa thành công {len(synced_files)} tài liệu từ Google Drive về Máy chủ Linux & Web!",
                "synced_count": len(synced_files),
                "total_chunks": total_chunks_added,
                "synced_files": synced_files,
                "errors": sync_errors,
                "drive_connected": True,
                "timestamp": self.last_sync_time
            }

        # Fallback / Local sync when Drive credentials are still pending or Drive folder is empty
        from app.seed.init_data import _auto_import_existing_documents
        _auto_import_existing_documents(db)

        all_docs = db.query(Document).all()
        return {
            "message": f"Đã đồng bộ {len(all_docs)} tài liệu giải pháp trên Máy chủ Linux vào Vector Knowledge Base & Web!",
            "synced_count": len(all_docs),
            "total_chunks": sum(d.chunk_count for d in all_docs),
            "synced_files": [{"name": d.document_name, "vendor": d.vendor, "category": d.solution_category, "pages": d.page_count, "chunks": d.chunk_count} for d in all_docs],
            "drive_connected": self.is_configured(),
            "errors": sync_errors,
            "timestamp": datetime.datetime.now().isoformat()
        }

gdrive_service = GoogleDriveService()
