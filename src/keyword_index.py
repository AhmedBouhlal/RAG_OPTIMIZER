from rank_bm25 import BM25Okapi


def build_bm25_index(input_dict):

    chunks = input_dict["chunks"]

    corpus = [chunk["text"].split() for chunk in chunks]

    bm25 = BM25Okapi(corpus)

    return {
        "bm25": bm25,
        "chunks": chunks
    }

def bm25_search(input_dict):

    query = input_dict["query"]
    bm25 = input_dict["bm25"]
    chunks = input_dict["chunks"]
    top_k = input_dict["top_k"]

    tokenized_query = query.split()

    scores = bm25.get_scores(tokenized_query)

    ranked = sorted(
        zip(chunks, scores),
        key=lambda x: x[1],
        reverse=True
    )[:top_k]

    results = []

    for chunk, score in ranked:
        results.append({
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "score": float(score)
        })

    return {"results": results}