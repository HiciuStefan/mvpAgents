# document_processing.py
from io import BytesIO
import PyPDF2

def extract_text_from_pdf(file_bytes):
    """
    Given a PDF file in bytes, this function returns its text content.
    """
    pdfReader = PyPDF2.PdfReader(BytesIO(file_bytes))
    text = ""
    for page in pdfReader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

# For Google Docs, one approach is to export the doc as plain text.
# This requires using the Drive API to export the file.
def export_google_doc_as_text(service, file_id):
    """
    Exports a Google Doc file as plain text.
    """
    request = service.files().export_media(fileId=file_id, mimeType='text/plain')
    text = request.execute().decode('utf-8')
    return text
