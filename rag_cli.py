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
from openai import OpenAI

# -----------------------------
# Load OpenAI API Key
# -----------------------------
try:
    with open("secret_key.json", "r") as f:
        secrets = json.load(f)
    os.environ["OPENAI_API_KEY"] = secrets["OPENAI_API_KEY"]
except FileNotFoundError:
    raise RuntimeError("secret_key.json not found! Please create it with your OpenAI API key.")

# -----------------------------
# Load Documents
# -----------------------------
docs = load_documents({"data_dir": "data/documents"}).get("documents", [])
if not docs:
    raise RuntimeError("No documents found in data/documents folder!")

# -----------------------------
# Load Best RAG Configuration
# -----------------------------
with open("results/summary.json", "r", encoding="utf-8") as f:
    summary = json.load(f)

best_config = summary["best_config"]

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
    context = "\n\n".join([r.get("text", "") for r in retrieval_results.get("results", [])])
    if not context:
        return "No relevant context found to answer this query."

    prompt = f"""
Answer the question based ONLY on the context.

Context:
{context}

Question: {query}

Answer:
"""
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating answer: {e}"

# -----------------------------
# Interactive CLI
# -----------------------------
print("\n=== Hybrid RAG Interactive CLI ===")
print("Type 'exit' to quit.\n")

while True:
    query = input("Query: ").strip()
    if query.lower() in ["exit", "quit"]:
        break
    if not query:
        continue

    # Hybrid retrieval (vector + BM25)
    retrieval = hybrid_retrieve({
        "query": query,
        "config": best_config,
        "index": index_dict["index"],
        "chunks": index_dict["chunks"],
        "bm25": bm25_index["bm25"]
    })

    # Take top 20 for reranking
    candidate_chunks = retrieval.get("results", [])[:20]
    reranked = reranker.rerank(query, candidate_chunks, top_k=best_config["top_k"])
    retrieval["results"] = reranked

    print("\nTop Retrieved Chunks:")
    for r in reranked:
        print(f"{r.get('chunk_id','N/A')} | score={r.get('score',0):.4f}")

    # Generate answer
    answer = rag_generate(query, retrieval)
    print("\nGenerated Answer:")
    print(answer)
    print("\n" + "-"*50 + "\n")