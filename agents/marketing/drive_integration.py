# drive_integration.py
import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
import io
from dotenv import load_dotenv

# The scopes define what permissions we need. Here we need read-only access.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
load_dotenv()
secrets_path = os.getenv("CLIENT_SECRETS_PATH")
def get_drive_service():
    """Authenticates and returns a Google Drive API service."""
    creds = None
    # token.pickle stores the user's access and refresh tokens.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # flow = InstalledAppFlow.from_client_secrets_file(
            #     os.path.join('credentials', 'client_secrets.json'), SCOPES)
            flow = InstalledAppFlow.from_client_secrets_file(secrets_path, SCOPES)
            creds = flow.run_local_server(port=3000)
        # Save the credentials for the next run.
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('drive', 'v3', credentials=creds)
    return service

def list_drive_files(service, page_size=10):
    """
    Lists up to `page_size` files from the user's Google Drive.
    Returns a list of dictionaries containing file id, name, and mimeType.
    """
    results = service.files().list(
        pageSize=page_size, fields="nextPageToken, files(id, name, mimeType)").execute()
    items = results.get('files', [])
    return items

def download_drive_file(service, file_id, file_path):
    """
    Downloads a file from Google Drive using its file_id and saves it to file_path.
    """
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    fh.close()
