import os
import json
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import mimetypes

# Get credentials and folder ID from environment
creds_json = os.getenv('GOOGLE_CREDENTIALS')
folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')

# Create credentials from JSON
creds_dict = json.loads(creds_json)
credentials = Credentials.from_service_account_info(
    creds_dict,
    scopes=['https://www.googleapis.com/auth/drive']
)

# Build Google Drive service
drive_service = build('drive', 'v3', credentials=credentials)

# Upload files from repo to Google Drive
def upload_file(file_path, folder_id):
    file_name = os.path.basename(file_path)
    
    # Check if file already exists in Drive
    query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
    results = drive_service.files().list(q=query, spaces='drive', fields='files(id)').execute()
    existing_files = results.get('files', [])
    
    if existing_files:
        # Update existing file
        file_id = existing_files[0]['id']
        media = MediaFileUpload(file_path, resumable=True)
        drive_service.files().update(fileId=file_id, media_body=media).execute()
        print(f"Updated: {file_name}")
    else:
        # Create new file
        file_metadata = {'name': file_name, 'parents': [folder_id]}
        media = MediaFileUpload(file_path, resumable=True)
        drive_service.files().create(body=file_metadata, media_body=media).execute()
        print(f"Uploaded: {file_name}")

# Walk through repo and upload files
for root, dirs, files in os.walk('.'):
    # Skip hidden directories and .git
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    
    for file in files:
        if not file.startswith('.'):
            file_path = os.path.join(root, file)
            upload_file(file_path, folder_id)

print("Sync complete!")
