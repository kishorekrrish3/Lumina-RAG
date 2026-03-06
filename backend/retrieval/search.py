import os
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VECTOR_STORE_DIR = os.path.join(BASE_DIR, "vector_store")

model = SentenceTransformer("all-MiniLM-L6-v2")

index = None
metadata = None

def reload_index():
    global index, metadata
    if os.path.exists(os.path.join(VECTOR_STORE_DIR, "paper_index.faiss")):
        index = faiss.read_index(os.path.join(VECTOR_STORE_DIR, "paper_index.faiss"))
        with open(os.path.join(VECTOR_STORE_DIR, "metadata.pkl"), "rb") as f:
            metadata = pickle.load(f)
    else:
        index = None
        metadata = []

reload_index()


def search(query, k=5):

    if index is None or not metadata:
        print("Warning: Vector index is empty. Please run ingestion to build the database.")
        return []

    query_embedding = model.encode([query])

    distances, indices = index.search(np.array(query_embedding), k)

    results = []

    for i in indices[0]:
        results.append(metadata[i])

    return results


if __name__ == "__main__":

    query = "How do transformers work?"

    results = search(query)

    for r in results:
        print("\nSource:", r["paper"])
        print(r["text"][:300])