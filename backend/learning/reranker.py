from sentence_transformers import CrossEncoder

# load reranker model
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank(query, docs):

    if not docs:
        return []

    pairs = [(query, doc["text"]) for doc in docs]
    scores = reranker.predict(pairs)

    for i in range(len(docs)):
        docs[i]["score"] = float(scores[i])

    ranked = sorted(
        docs,
        key=lambda x: x["score"],
        reverse=True
    )

    return ranked