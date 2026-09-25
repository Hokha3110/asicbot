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
        return settings.GOOGLE_DRIVE_FOLDER_ID or "1vk4wIUrIXJ7LwlTLuoyhq8h2w4Dpc0Ra"

    def _get_drive_service(self, custom_sa_json: Optional[str] = None):
        """
        Initializes Google Drive API v3 client using:
        1. OAuth2 User Credentials (google_drive_tokens.json)
        2. Service Account credentials (service_account.json or GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON)
        """
        try:
            from googleapiclient.discovery import build
            from google.oauth2 import credentials as oauth_credentials
            from google.oauth2 import service_account

            SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.readonly']

            # 1. Check OAuth2 token file generated after user logs in with Google
            token_candidates = [
                getattr(settings, 'GOOGLE_DRIVE_TOKENS_PATH', './google_drive_tokens.json'),
                "./google_drive_tokens.json",
                "../google_drive_tokens.json",
                "./backend/google_drive_tokens.json"
            ]
            for t_path in token_candidates:
                if os.path.exists(t_path):
                    try:
                        with open(t_path, "r", encoding="utf-8") as tf:
                            t_data = json.load(tf)
                            if t_data.get("access_token") or t_data.get("refresh_token"):
                                creds = oauth_credentials.Credentials(
                                    token=t_data.get("access_token"),
                                    refresh_token=t_data.get("refresh_token"),
                                    token_uri=t_data.get("token_uri", "https://oauth2.googleapis.com/token"),
                                    client_id=t_data.get("client_id", settings.GOOGLE_CLIENT_ID),
                                    client_secret=t_data.get("client_secret", settings.GOOGLE_CLIENT_SECRET),
                                    scopes=SCOPES
                                )
                                self._service = build('drive', 'v3', credentials=creds)
                                return self._service
                    except Exception as e:
                        print(f"[GoogleDriveService] OAuth token load notice: {e}")

            # 2. Check custom JSON passed directly
            if custom_sa_json and custom_sa_json.strip().startswith('{'):
                try:
                    info = json.loads(custom_sa_json)
                    if info.get("type") == "service_account":
                        creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
                        self._service = build('drive', 'v3', credentials=creds)
                        return self._service
                except Exception:
                    pass

            # 3. Check direct JSON string in settings
            if settings.GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON and settings.GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON.strip().startswith('{'):
                try:
                    info = json.loads(settings.GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON)
                    if info.get("type") == "service_account":
                        creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
                        self._service = build('drive', 'v3', credentials=creds)
                        return self._service
                except Exception:
                    pass
            
            # 4. Check service_account.json file path
            sa_candidates = [
                settings.GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH,
                "./service_account.json",
                "../service_account.json",
                "./backend/service_account.json"
            ]
            for sa_path in sa_candidates:
                if os.path.exists(sa_path):
                    try:
                        with open(sa_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if data.get("type") == "service_account":
                                creds = service_account.Credentials.from_service_account_info(data, scopes=SCOPES)
                                self._service = build('drive', 'v3', credentials=creds)
                                return self._service
                    except Exception as e:
                        print(f"[GoogleDriveService] SA check notice: {e}")

        except Exception as e:
            print(f"[GoogleDriveService] Init notice: {e}")

        return None

    def is_configured(self) -> bool:
        service = self._get_drive_service()
        return service is not None

    def _resolve_folder_id(self, service, folder_id: Optional[str] = None) -> Optional[str]:
        """
        Validates folder ID and provides smart auto-correction if typo or casing difference.
        """
        target_folder = folder_id.strip() if (folder_id and folder_id.strip()) else self.get_folder_id()
        if not target_folder:
            return None

        # 1. Try direct check
        try:
            folder_meta = service.files().get(
                fileId=target_folder,
                supportsAllDrives=True,
                fields="id, name, mimeType"
            ).execute()
            if folder_meta:
                return target_folder
        except Exception:
            pass

        # 2. Try search by name fallback for ASIC folder
        try:
            res = service.files().list(
                q="name = 'TÀI LIỆU ASIC' and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields="files(id, name)"
            ).execute()
            found = res.get('files', [])
            if found:
                return found[0]['id']
        except Exception:
            pass

        return target_folder

    def test_connection(self, folder_id: Optional[str] = None, sa_json: Optional[str] = None) -> Dict[str, Any]:
        """
        Tests connection to Google Drive API and verifies folder accessibility.
        """
        service = self._get_drive_service(sa_json)
        if not service:
            return {
                "success": False,
                "message": "Chưa kết nối Google Drive. Vui lòng bấm 'Đăng nhập Google để kết nối Drive'."
            }

        resolved_folder = self._resolve_folder_id(service, folder_id)
        try:
            if resolved_folder:
                folder_meta = service.files().get(
                    fileId=resolved_folder,
                    supportsAllDrives=True,
                    fields="id, name, mimeType"
                ).execute()
                return {
                    "success": True,
                    "message": f"Kết nối Google Drive thành công! Đã tìm thấy thư mục: '{folder_meta.get('name', resolved_folder)}'",
                    "folder_name": folder_meta.get("name"),
                    "folder_id": resolved_folder
                }
            else:
                about = service.about().get(fields="user").execute()
                return {
                    "success": True,
                    "message": f"Kết nối Google Drive thành công qua tài khoản Google!",
                    "user": about.get("user")
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Lỗi khi truy cập Google Drive: {str(e)}"
            }

    def list_files_in_folder(self, folder_id: Optional[str] = None, sa_json: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lists all document files (PDF, DOCX, PPTX, XLSX, TXT, Google Docs) in the Google Drive folder.
        """
        service = self._get_drive_service(sa_json)
        if not service:
            return []

        resolved_folder = self._resolve_folder_id(service, folder_id)
        all_files = []
        page_token = None

        try:
            query = f"'{resolved_folder}' in parents and trashed = false" if resolved_folder else "trashed = false"
            while True:
                results = service.files().list(
                    q=query,
                    pageSize=100,
                    pageToken=page_token,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
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
                request = service.files().get_media(fileId=file_id, supportsAllDrives=True)

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
                file_size = int(f.get('size', 0)) if f.get('size') else 0

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

        # Fallback notice if Drive is not yet connected
        is_drive_active = self.is_configured()
        if not is_drive_active:
            return {
                "message": "Chưa kết nối Google Drive. Vui lòng bấm 'Đăng nhập Google để kết nối Drive'.",
                "synced_count": 0,
                "total_chunks": 0,
                "synced_files": [],
                "errors": ["Chưa xác thực Google Drive OAuth2 hoặc Service Account."],
                "drive_connected": False,
                "timestamp": datetime.datetime.now().isoformat()
            }

        return {
            "message": "Thư mục Google Drive trống hoặc không tìm thấy tài liệu phù hợp (PDF, DOCX, PPTX).",
            "synced_count": 0,
            "total_chunks": 0,
            "synced_files": [],
            "drive_connected": True,
            "errors": sync_errors,
            "timestamp": datetime.datetime.now().isoformat()
        }

gdrive_service = GoogleDriveService()
