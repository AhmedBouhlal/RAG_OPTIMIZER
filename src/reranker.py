from sentence_transformers import CrossEncoder


class Reranker:

    def __init__(self, model_name="BAAI/bge-reranker-base"):
        self.model = CrossEncoder(model_name)

    def rerank(self, query, chunks, top_k=5):

        pairs = [(query, chunk["text"]) for chunk in chunks]

        scores = self.model.predict(pairs)

        results = []

        for chunk, score in zip(chunks, scores):
            results.append({
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "score": float(score)
            })

        ranked = sorted(results, key=lambda x: x["score"], reverse=True)

        return ranked[:top_k]