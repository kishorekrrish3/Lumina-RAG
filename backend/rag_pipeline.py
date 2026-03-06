from retrieval.search import search, reload_index
from learning.reranker import rerank
from generation.gemini_generator import generate_answer
from ingestion.arxiv_fetcher import fetch_papers
from ingestion.update_vector_db import update_vector_db

# CrossEncoder: scores below this indicate weak/irrelevant context
WEAK_SCORE_THRESHOLD = -2.0


def is_weak_retrieval(ranked_docs: list) -> bool:
    """Returns True if the retrieved docs are likely irrelevant."""
    if not ranked_docs:
        return True
    top_score = ranked_docs[0].get("score", 0)
    return top_score < WEAK_SCORE_THRESHOLD


def background_fetch_and_index(query: str):
    """
    Runs AFTER a response is already sent to the user.
    Downloads new papers from arXiv and updates the FAISS index
    so future queries on this topic will be answered from local DB.
    """
    try:
        print(f"[Background] Fetching arXiv papers for: '{query}'")
        new_files = fetch_papers(query, max_results=3)

        if new_files:
            update_vector_db(new_files)
            reload_index()
            print(f"[Background] Knowledge base updated with {len(new_files)} new paper(s).")
        else:
            print("[Background] No new papers to index (already cached).")
    except Exception as e:
        print(f"[Background] arXiv fetch failed (non-critical): {e}")


def rag_query(query: str):
    """
    Main RAG pipeline. Returns (answer, sources, needs_background_fetch).
    The caller is responsible for scheduling background_fetch_and_index
    if needs_background_fetch is True.
    """
    # Step 1: Retrieve from local FAISS
    results = search(query, k=10)

    if not results:
        # No local docs at all — signal caller to background fetch
        return (
            "I don't have enough information locally yet. I'm fetching relevant research papers in the background — please ask again in a moment!",
            [],
            True,
        )

    # Step 2: Rerank
    ranked_docs = rerank(query, results)

    # Step 3: Check quality
    weak = is_weak_retrieval(ranked_docs)

    # Step 4: Generate answer from best available context (don't wait for arXiv)
    top_docs = ranked_docs[:5]
    contexts = [doc["text"] for doc in top_docs]
    answer = generate_answer(query, contexts)
    sources = list(set([doc["paper"] for doc in top_docs]))

    return answer, sources, weak