# main.py
import streamlit as st
import io

# Import our modules
from drive_integration import get_drive_service, list_drive_files, download_drive_file
from document_processing import extract_text_from_pdf, export_google_doc_as_text
from agents._tools.llm_marketingAgent  import generate_marketing_strategy

st.set_page_config(page_title="AI Marketing Agent", layout="wide")
st.title("AI Marketing Agent")

# Sidebar: Option to choose source of document
st.sidebar.header("Select Document Source")
source_option = st.sidebar.radio("Choose file source", ("Upload a File", "Select from Google Drive"))

document_text = ""

if source_option == "Upload a File":
    uploaded_file = st.file_uploader("Upload your marketing document (PDF or TXT)", type=["pdf", "txt"])
    if uploaded_file is not None:
        file_type = uploaded_file.name.split('.')[-1].lower()
        if file_type == "txt":
            document_text = uploaded_file.read().decode("utf-8")
        elif file_type == "pdf":
            file_bytes = uploaded_file.read()
            document_text = extract_text_from_pdf(file_bytes)
        
        st.subheader("Extracted Document Content")
        st.text_area("Review Document", document_text, height=300)

elif source_option == "Select from Google Drive":
    st.write("Connecting to Google Drive...")
    drive_service = get_drive_service()
    files = list_drive_files(drive_service)
    if not files:
        st.write("No files found in Google Drive.")
    else:
        # Create a dropdown of file names
        file_names = {file["name"]: file for file in files}
        selected_file_name = st.selectbox("Select a file:", list(file_names.keys()))
        selected_file = file_names[selected_file_name]
        file_id = selected_file["id"]
        
        # Check MIME type to decide how to process the file.
        if "application/pdf" in selected_file["mimeType"]:
            # Download file bytes.
            # Save temporarily as "temp.pdf"
            temp_file = "temp.pdf"
            download_drive_file(drive_service, file_id, temp_file)
            with open(temp_file, "rb") as f:
                file_bytes = f.read()
            document_text = extract_text_from_pdf(file_bytes)
        elif "application/vnd.google-apps.document" in selected_file["mimeType"]:
            # Export Google Doc as plain text
            document_text = export_google_doc_as_text(drive_service, file_id)
        else:
            st.write("Unsupported file type.")
        
        st.subheader("Extracted Document Content")
        st.text_area("Review Document", document_text, height=300)

# Button to generate marketing strategy
if document_text:
    if st.button("Generate Marketing Strategy"):
        with st.spinner("Generating strategy..."):
            strategy_draft = generate_marketing_strategy(document_text)
        st.subheader("Draft Marketing Strategy")
        # Provide a text area for review and feedback
        final_strategy = st.text_area("Edit the generated strategy as needed:", strategy_draft, height=300)
        if st.button("Finalize Strategy"):
            st.success("Marketing Strategy Finalized!")
            st.write(final_strategy)
