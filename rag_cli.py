from src.loader import load_documents
from src.chunking import chunk_documents
from src.embedding import generate_embeddings
from src.vectordb import build_index
from src.experiment import get_best_config
from src.keyword_index import build_bm25_index
from src.hybrid_retrieval import hybrid_retrieve
from src.reranker import Reranker

import json
import os
import openai

# -----------------------------
# Load OpenAI API Key
# -----------------------------
with open("secret_key.json", "r") as f:
    secrets = json.load(f)

os.environ["OPENAI_API_KEY"] = secrets["OPENAI_API_KEY"]

# -----------------------------
# Load Documents
# -----------------------------
docs = load_documents({"data_dir": "data/documents"})["documents"]

# -----------------------------
# Load Best RAG Configuration
# -----------------------------
summary = get_best_config("results")
best_config = summary["best_config"]

print("Using best config:", best_config)

# -----------------------------
# Chunk Documents
# -----------------------------
chunks = chunk_documents({
    "documents": docs,
    "config": {
        "chunk_size": best_config["chunk_size"],
        "overlap": best_config["overlap"]
    }
})

# -----------------------------
# Generate Embeddings
# -----------------------------
embeddings = generate_embeddings({
    "chunks": chunks["chunks"],
    "config": {"embedding_model": best_config["embedding_model"]}
})

# -----------------------------
# Build Vector Index
# -----------------------------
index_dict = build_index({
    "chunks": chunks["chunks"],
    "embeddings": embeddings["embeddings"]
})

# -----------------------------
# Build BM25 Index (Keyword Search)
# -----------------------------
bm25_index = build_bm25_index({
    "chunks": chunks["chunks"]
})

# -----------------------------
# Initialize Reranker
# -----------------------------
reranker = Reranker()  # default model: "BAAI/bge-reranker-base"

# -----------------------------
# GPT Generation
# -----------------------------
def rag_generate(query, retrieval_results):

    context = "\n\n".join([r["text"] for r in retrieval_results["results"]])

    prompt = f"""
Answer the question based ONLY on the context.

Context:
{context}

Question: {query}

Answer:
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response["choices"][0]["message"]["content"]


# -----------------------------
# Interactive CLI
# -----------------------------
print("\n=== Hybrid RAG Interactive CLI ===")
print("Type 'exit' to quit.\n")

while True:

    query = input("Query: ")

    if query.lower() in ["exit", "quit"]:
        break

    retrieval = hybrid_retrieve({
    "query": query,
    "config": best_config,
    "index": index_dict["index"],
    "chunks": index_dict["chunks"],
    "bm25": bm25_index["bm25"]
})

    # take top 20 for reranking
    candidate_chunks = retrieval["results"][:20]

    reranked = reranker.rerank(query, candidate_chunks, top_k=best_config["top_k"])

    retrieval = {"results": reranked}

    print("\nTop Retrieved Chunks:")

    for r in retrieval["results"]:
        print(f"{r['chunk_id']} | score={r['score']:.4f}")

    answer = rag_generate(query, retrieval)

    print("\nGenerated Answer:")
    print(answer)
    print("\n" + "-"*50 + "\n")