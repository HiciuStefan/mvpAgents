import base64
import logging
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
import re

def get_plain_text_from_payload(payload,level=0):
    """
    Recursively scans a payload (or part of an email) for any part
    with a 'text/plain' MIME type and decodes its contents.
    
    Returns:
        A string with all plain text concatenated.
    """
    text_content = ""

    # First, check if the payload itself has 'parts' (i.e. it's multipart)
    if 'parts' in payload:
        for part in payload['parts']:
            # Recursively extract text from each sub-part and add it to the result.
            text_content += get_plain_text_from_payload(part, level + 1)
    else:
        mime = payload.get('mimeType', '')
        data = payload.get('body', {}).get('data', '')
        if data:
            try:
                decoded_text = base64.urlsafe_b64decode(data.encode('UTF-8')).decode('UTF-8')
            except Exception as e:
                print("Error decoding text:", e)
                decoded_text = ""
            
            # For single-layer messages (level == 0), check for text/plain first,
            # if not, fallback to text/html.
            if mime == 'text/plain':
                text_content += decoded_text
            elif level == 0 and mime == 'text/html':
                soup = BeautifulSoup(decoded_text, "html.parser")
                cleaned_text = soup.get_text(separator=" ")  # Keeps word spacing

                # Remove excessive spaces, newlines, and unwanted characters
                cleaned_text = re.sub(r'[\r\n\t]+', ' ', cleaned_text)  # Replace \n, \r, \t with spaces
                cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()  # Remove excessive spaces

                text_content += cleaned_text
            # For nested parts (level > 0), ignore HTML.
    return text_content

def get_emails(creds, max_results=50):
    service = build('gmail', 'v1', credentials=creds)
    emails = []
    next_page_token = None

    while True:

        try:
            results = service.users().messages().list(userId='me', q="is:unread",labelIds=['UNREAD'],maxResults=max_results,pageToken=next_page_token).execute()

            for msg in results.get('messages', []):
                # Request the full email content.
                email_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            
                # Get subject from headers.
                headers = email_data['payload'].get('headers', [])
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), "(No Sender)")
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), "(No Subject)")
                snippet = email_data.get('snippet', '')
            
                payload = email_data.get('payload', {})
                # Use the recursive function to extract the full body text.
                full_body = get_plain_text_from_payload(payload)

                emails.append({
                    'id': msg['id'],
                    'subject': subject,
                    'sender': sender.split("<")[0].strip(),  
                    'body': full_body,  # Now this is the entire plain text from all parts.
                    'snippet': snippet,
                    'labelIds': email_data.get('labelIds', []),
                })


            next_page_token = results.get('nextPageToken')
            if not next_page_token:  # Stop if no more pages
                break
        except Exception as e:
            logging.error(f"Error fetching emails: {str(e)}")
            return []
    return emails