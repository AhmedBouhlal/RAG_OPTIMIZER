from sentence_transformers import SentenceTransformer
from src.vectordb import search_index

def retrieve_chunks(input_dict):

    query = input_dict["query"]
    config = input_dict["config"]
    index = input_dict["index"]
    chunks = input_dict["chunks"]

    top_k = config["top_k"]
    model_name = config["embedding_model"]

    # 1️⃣ Load embedding model
    model = SentenceTransformer(model_name)

    # 2️⃣ Encode query
    query_vector = model.encode([query])[0].tolist()

    # 3️⃣ Search index
    search_input = {
        "index": index,
        "query_vector": query_vector,
        "top_k": top_k
    }

    search_results = search_index(search_input)

    # 4️⃣ Map chunk_id → chunk text
    chunk_map = {c["chunk_id"]: c["text"] for c in chunks}

    results = []
    for r in search_results["results"]:
        chunk_id = r["chunk_id"]
        results.append({
            "chunk_id": chunk_id,
            "score": r["score"],
            "text": chunk_map.get(chunk_id, "")
        })

    output = {
        "query": query,
        "results": results
    }

    return output
