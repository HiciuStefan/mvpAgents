import os
import fitz  # PyMuPDF
import docx2txt


def get_all_files(FOLDER_NAME):
    files = []
    for root, _, filenames in os.walk(FOLDER_NAME):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            files.append(file_path)
    return files



def read_pdf_text(file_path):
	text = ""
	doc = fitz.open(file_path)
	for page in doc:
		text += page.get_text()
	return text


def read_docx_text(file_path):
    print(file_path)
    text = docx2txt.process(file_path)
    return text