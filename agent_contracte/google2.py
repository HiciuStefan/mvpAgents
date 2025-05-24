import os
import io
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from io import BytesIO

# If modifying scopes, delete the token.json file
SCOPES = ['https://www.googleapis.com/auth/drive']


def list_file_permissions(service, file_id):
    try:
        permissions = service.permissions().list(fileId=file_id).execute()
        print(f"Permissions for file {file_id}:")
        for p in permissions.get('permissions', []):
            print(f" - ID: {p.get('id')}, Type: {p.get('type')}, Role: {p.get('role')}, Email: {p.get('emailAddress', 'N/A')}")
    except Exception as e:
        print(f"Failed to list permissions: {e}")

def get_from_g_drive():
    os.makedirs('downloads', exist_ok=True)
    creds = None
    # The file token.json stores the user's access and refresh tokens
    try:
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    except:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('drive', 'v3', credentials=creds)


    folder_id = '1tHY91mYUEaZ3opeZIxUETPyHctOkSTu2'  # replace this with your folder ID

    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, pageSize=100, fields="files(id, name)").execute()
    items = results.get('files', [])


    if not items:
        print("No files found.")
    else:
        print("Checking and downloading files...")
        for item in items:
            print(item['id'])
            file_id = item['id']
            list_file_permissions(service, file_id)
            file_name = item['name']
            file_path = os.path.join('downloads', file_name)

            # Check if file already exists
            if os.path.exists(file_path):
                print(f"Skipping (already exists): {file_name}")
                continue

            # Download the file
            request = service.files().get_media(fileId=file_id)
            fh = io.FileIO(file_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    print(f"Downloading {file_name} ({int(status.progress() * 100)}%)")

# if __name__ == '__main__':
#     main()