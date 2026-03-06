import os
import faiss
import numpy as np
import pickle
import pdfplumber
from chunker import chunk_text
from embedder import generate_embeddings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data", "papers")
VECTOR_STORE_DIR = os.path.join(BASE_DIR, "vector_store")

def load_pdfs_safe(folder_path):
    """Load PDFs with page cap to avoid hanging on massive files."""
    documents = []
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            path = os.path.join(folder_path, file)
            try:
                with pdfplumber.open(path) as pdf:
                    text = ""
                    for page in pdf.pages[:15]:  # cap at 15 pages
                        try:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text
                        except Exception:
                            pass
                if text.strip():
                    documents.append({"paper": file, "text": text})
                    print(f"  Loaded: {file}")
                else:
                    print(f"  Skipped (no text): {file}")
            except Exception as e:
                print(f"  Error loading {file}: {e}")
    return documents

def build_vector_store():
    print(f"Loading PDFs from: {DATA_PATH}")
    documents = load_pdfs_safe(DATA_PATH)
    print(f"Loaded {len(documents)} documents.")

    all_chunks = []
    metadata = []

    for doc in documents:
        chunks = chunk_text(doc["text"])
        for chunk in chunks:
            all_chunks.append(chunk)
            metadata.append({"paper": doc["paper"], "text": chunk})

    print(f"Generating embeddings for {len(all_chunks)} chunks...")
    embeddings = generate_embeddings(all_chunks)

    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    faiss.write_index(index, os.path.join(VECTOR_STORE_DIR, "paper_index.faiss"))

    with open(os.path.join(VECTOR_STORE_DIR, "metadata.pkl"), "wb") as f:
        pickle.dump(metadata, f)

    print(f"Vector database built successfully! ({len(all_chunks)} chunks across {len(documents)} papers)")


if __name__ == "__main__":
    build_vector_store()