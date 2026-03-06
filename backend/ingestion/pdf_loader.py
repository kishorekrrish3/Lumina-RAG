import pdfplumber
import os

def load_pdfs(folder_path):
    documents = []

    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            path = os.path.join(folder_path, file)

            with pdfplumber.open(path) as pdf:
                text = ""

                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text

                documents.append({
                    "paper": file,
                    "text": text
                })

    return documents