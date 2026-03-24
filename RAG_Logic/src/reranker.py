from sentence_transformers import CrossEncoder
import torch


class Reranker:

    def __init__(self, model_name="BAAI/bge-reranker-base"):
        # Check for CUDA availability and use it if available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🎯 Reranker using device: {device}")

        self.model = CrossEncoder(model_name, device=device)

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