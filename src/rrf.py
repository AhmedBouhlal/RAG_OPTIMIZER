def reciprocal_rank_fusion(semantic_results, keyword_results, k=60):

    fused = {}

    # semantic ranking
    for rank, item in enumerate(semantic_results):
        chunk_id = item["chunk_id"]

        score = 1 / (k + rank + 1)

        if chunk_id not in fused:
            fused[chunk_id] = {
                "chunk_id": chunk_id,
                "text": item["text"],
                "score": 0
            }

        fused[chunk_id]["score"] += score

    # keyword ranking
    for rank, item in enumerate(keyword_results):
        chunk_id = item["chunk_id"]

        score = 1 / (k + rank + 1)

        if chunk_id not in fused:
            fused[chunk_id] = {
                "chunk_id": chunk_id,
                "text": item["text"],
                "score": 0
            }

        fused[chunk_id]["score"] += score

    ranked = sorted(
        fused.values(),
        key=lambda x: x["score"],
        reverse=True
    )

    return ranked