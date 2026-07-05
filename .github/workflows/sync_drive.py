import os
import json
import sys
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

print("=" * 50)
print("GOOGLE DRIVE SYNC - DIAGNOSTIC MODE")
print("=" * 50)

# Get credentials and folder ID from environment
creds_json = os.getenv('GOOGLE_CREDENTIALS')
folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')

print(f"\n[1] Environment Check:")
print(f"    Credentials set: {bool(creds_json)}")
print(f"    Folder ID: {folder_id}")

print(f"\n[2] Files in repository:")
file_count = 0
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    for file in files:
        if not file.startswith('.'):
            file_path = os.path.join(root, file)
            print(f"    - {file_path}")
            file_count += 1

print(f"    Total: {file_count} files")

if not creds_json or not folder_id:
    print("\n[ERROR] Missing GOOGLE_CREDENTIALS or GOOGLE_DRIVE_FOLDER_ID")
    sys.exit(1)

try:
    print(f"\n[3] Authentication:")
    creds_dict = json.loads(creds_json)
    print(f"    Service: {creds_dict.get('client_email')}")
    
    credentials = Credentials.from_service_account_info(
        creds_dict,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    print(f"    ✓ Credentials loaded")

    drive_service = build('drive', 'v3', credentials=credentials)
    print(f"    ✓ Drive service ready")

    print(f"\n[4] Testing folder access:")
    folder = drive_service.files().get(fileId=folder_id, fields='name').execute()
    print(f"    ✓ Folder: {folder.get('name')}")

    print(f"\n[5] Uploading files:")
    uploaded = 0
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if not file.startswith('.'):
                file_path = os.path.join(root, file)
                file_name = os.path.basename(file_path)
                
                try:
                    file_metadata = {'name': file_name, 'parents': [folder_id]}
                    media = MediaFileUpload(file_path, resumable=True)
                    drive_service.files().create(body=file_metadata, media_body=media).execute()
                    print(f"    ✓ {file_path}")
                    uploaded += 1
                except Exception as e:
                    print(f"    ✗ {file_path}: {str(e)}")

    print(f"\n✓ Success! Uploaded {uploaded} files\n")

except Exception as e:
    print(f"\n✗ Error: {str(e)}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)
