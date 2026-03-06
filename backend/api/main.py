import sys
import os

# Add the backend directory to sys.path so modules can be imported relative to it
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from api.schemas import QueryRequest, FeedbackRequest
from rag_pipeline import rag_query, background_fetch_and_index
from feedback.feedback_logger import log_feedback

app = FastAPI(title="Lumina RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Lumina RAG API is running"}


@app.post("/ask")
def ask_question(request: QueryRequest, background_tasks: BackgroundTasks):
    try:
        answer, sources, needs_fetch = rag_query(request.query)

        # If retrieval was weak, schedule a background arXiv fetch.
        # This runs AFTER the response is returned — user is never blocked.
        if needs_fetch:
            background_tasks.add_task(background_fetch_and_index, request.query)
            print(f"[API] Weak retrieval detected. Background fetch scheduled for: '{request.query}'")

        return {
            "query": request.query,
            "answer": answer,
            "sources": sources,
        }
    except Exception as e:
        print(f"[API] Error during /ask: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback")
def feedback(request: FeedbackRequest):
    log_feedback(request.query, request.answer, request.feedback)
    return {"message": "Feedback recorded"}