from retrieval.search import search
from generation.gemini_generator import generate_answer


def research_agent(query):

    # Step 1 retrieve papers
    docs = search(query, k=10)

    contexts = [d["text"] for d in docs]

    # Step 2 ask Gemini to analyze papers
    prompt = f"""
You are an AI research analyst.

Analyze the following research paper excerpts and answer the question.

Question:
{query}

Context:
{contexts}

Provide:

1 Key explanation
2 Main research insights
3 Comparison of ideas
4 Final conclusion
"""

    answer = generate_answer(query, contexts)

    return answer, docs