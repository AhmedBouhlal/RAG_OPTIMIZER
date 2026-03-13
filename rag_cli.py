from src.loader import load_documents
from src.chunking import chunk_documents
from src.embedding import generate_embeddings
from src.vectordb import build_index
from src.retrieval import retrieve_chunks
from src.experiment import get_best_config
import json
import os

# Load key from file
with open("secret_key.json", "r") as f:
    secrets = json.load(f)

# Set environment variable (used by OpenAI library)
os.environ["OPENAI_API_KEY"] = secrets["OPENAI_API_KEY"]

# Load documents
docs = load_documents({"data_dir": "data/documents"})["documents"]

# Load best config
summary = get_best_config("results")
best_config = summary["best_config"]

# Precompute embeddings + index
chunks = chunk_documents({
    "documents": docs,
    "config": {"chunk_size": best_config["chunk_size"], "overlap": best_config["overlap"]}
})
embeddings = generate_embeddings({"chunks": chunks["chunks"], "config": {"embedding_model": best_config["embedding_model"]}})
index_dict = build_index({"chunks": chunks["chunks"], "embeddings": embeddings["embeddings"]})

import openai

def rag_generate(query, retrieval_results):
    # Combine top chunks into context
    context = "\n".join([r["text"] for r in retrieval_results["results"]])
    prompt = f"Answer the question based on the context below:\n\nContext:\n{context}\n\nQuestion: {query}\nAnswer:"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response["choices"][0]["message"]["content"]

print("=== RAG Interactive CLI ===")
while True:
    query = input("Query: ")
    if query.lower() in ["exit", "quit"]:
        break
    retrieval = retrieve_chunks({
        "query": query,
        "config": {"embedding_model": best_config["embedding_model"], "top_k": best_config["top_k"]},
        "index": index_dict["index"],
        "chunks": index_dict["chunks"]
    })
    answer = rag_generate(query, retrieval)
    print(f"Generated Answer: {answer}")
