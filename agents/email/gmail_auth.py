import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']


def authenticate_gmail():
    creds = None
    base_dir = os.path.dirname(os.path.abspath(__file__))
    credentials_path = os.path.join(base_dir, 'credentials.json')
    token_path = os.path.join(base_dir, 'token.json')

    # Check if token.json already exists (reuse credentials)
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            try:
            # If no valid credentials are available, let the user log in.
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)  # Ensure the credentials.json is available
                creds = flow.run_local_server(port=3000, access_type="offline", prompt="consent")  # This will open the browser for login
        
            except FileNotFoundError as e:
                raise FileNotFoundError(f"{e} file not found. Please provide the OAuth 2")
            
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds
