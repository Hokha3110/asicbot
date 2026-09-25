from app.services.gdrive_service import gdrive_service
import sys

sys.stdout.reconfigure(encoding='utf-8')

service = gdrive_service._get_drive_service()
exact_folder_id = "1vk4wIUrIXJ7LwlTLuoyhq8h2w4Dpc0Ra"

query = f"'{exact_folder_id}' in parents and trashed = false"
r = service.files().list(
    q=query,
    supportsAllDrives=True,
    includeItemsFromAllDrives=True,
    fields="files(id, name, mimeType, size, webViewLink)"
).execute()

files = r.get('files', [])
print(f"\nFiles found inside 'TÀI LIỆU ASIC' (ID: {exact_folder_id}): {len(files)}")
for f in files:
    print(f"  - [{f.get('name')}] (Mime: {f.get('mimeType')}, Size: {f.get('size')} bytes)")
