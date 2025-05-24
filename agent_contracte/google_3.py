import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive']

def create_service():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=8080)
    return build('drive', 'v3', credentials=creds)

def download_file(service, file_id, file_path):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()  # Use BytesIO for in-memory binary stream
    downloader = MediaIoBaseDownload(fd=fh, request=request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"Download Progress: {int(status.progress() * 100)}%")
    fh.seek(0)
    with open(file_path, 'wb') as f:
        f.write(fh.read())
    print(f"Downloaded to: {file_path}")

def list_file_permissions(service, file_id):
    try:
        permissions = service.permissions().list(fileId=file_id).execute()
        print(f"Permissions for file {file_id}:")
        for p in permissions.get('permissions', []):
            print(f" - ID: {p.get('id')}, Type: {p.get('type')}, Role: {p.get('role')}, Email: {p.get('emailAddress', 'N/A')}")
    except Exception as e:
        print(f"Failed to list permissions: {e}")

def add_viewer_permission(service, file_id, email):
    new_permission = {
        'type': 'user',
        'role': 'reader',
        'emailAddress': email,
    }
    try:
        service.permissions().create(
            fileId=file_id,
            body=new_permission,
            fields='id',
            sendNotificationEmail=False
        ).execute()
        print(f"Added viewer permission for {email} on file {file_id}")
    except Exception as e:
        print(f"Failed to add permission: {e}")

def main():
    service = create_service()

    folder_id = '1tHY91mYUEaZ3opeZIxUETPyHctOkSTu2'  # Your folder ID
    query = f"'{folder_id}' in parents and trashed=false"

    results = service.files().list(q=query, pageSize=100, fields="files(id, name)").execute()
    items = results.get('files', [])

    os.makedirs('downloads', exist_ok=True)

    if not items:
        print("No files found.")
        return

    print("Checking and downloading files...")

    for item in items:
        file_id = item['id']
        file_name = item['name']
        file_path = os.path.join('downloads', file_name)

        if os.path.exists(file_path):
            print(f"Skipping (already exists): {file_name}")
            continue

        # Optional: list permissions before download (helpful for debugging)
        # list_file_permissions(service, file_id)

        try:
            download_file(service, file_id, file_path)
        except Exception as e:
            print(f"Failed to download {file_name}: {e}")

main()