import os
import faiss
import pickle
import numpy as np
import pdfplumber
from ingestion.chunker import chunk_text
from ingestion.embedder import generate_embeddings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VECTOR_STORE_DIR = os.path.join(BASE_DIR, "vector_store")
INDEX_PATH = os.path.join(VECTOR_STORE_DIR, "paper_index.faiss")
META_PATH = os.path.join(VECTOR_STORE_DIR, "metadata.pkl")

def update_vector_db(new_files=None):
    if not new_files:
        print("No new files to index.")
        return
        
    documents = []
    
    for filepath in new_files:
        if filepath.endswith(".pdf") and os.path.exists(filepath):
            filename = os.path.basename(filepath)
            with pdfplumber.open(filepath) as pdf:
                text = ""
                # Read only up to 10 pages to prevent heavy processing delays
                for page in pdf.pages[:10]:
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text
                    except Exception as e:
                        print(f"Error reading page in {filename}: {e}")
                
                documents.append({
                    "paper": filename,
                    "text": text
                })

    if not documents:
        return

    chunks = []
    new_metadata = []

    for doc in documents:
        text_chunks = chunk_text(doc["text"])
        for c in text_chunks:
            chunks.append(c)
            new_metadata.append({
                "paper": doc["paper"],
                "text": c
            })

    embeddings = generate_embeddings(chunks)
    embeddings = np.array(embeddings)
    
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    
    # Reload existing index or create new one if not exists
    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
    else:
        dimension = len(embeddings[0])
        index = faiss.IndexFlatL2(dimension)
        
    index.add(embeddings)
    faiss.write_index(index, INDEX_PATH)
    
    # Reload existing metadata
    metadata = []
    if os.path.exists(META_PATH):
        with open(META_PATH, "rb") as f:
            metadata = pickle.load(f)
            
    metadata.extend(new_metadata)
    
    with open(META_PATH, "wb") as f:
        pickle.dump(metadata, f)

    print(f"Vector DB Updated with {len(documents)} new papers.")