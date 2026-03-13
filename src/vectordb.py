import numpy as np


def build_index(input_dict):

    embeddings = input_dict["embeddings"]
    chunks = input_dict["chunks"]

    vectors = []
    chunk_ids = []

    for item in embeddings:

        vectors.append(item["vector"])
        chunk_ids.append(item["chunk_id"])

    vectors = np.array(vectors)

    index = {
        "vectors": vectors,
        "chunk_ids": chunk_ids
    }

    output = {
        "index": index,
        "chunks": chunks
    }

    return output

def cosine_similarity(query_vector, matrix):

    query = np.array(query_vector)

    dot = np.dot(matrix, query)

    query_norm = np.linalg.norm(query)
    matrix_norm = np.linalg.norm(matrix, axis=1)

    similarity = dot / (matrix_norm * query_norm)

    return similarity

def search_index(input_dict):

    index = input_dict["index"]
    query_vector = input_dict["query_vector"]
    top_k = input_dict["top_k"]

    vectors = index["vectors"]
    chunk_ids = index["chunk_ids"]

    scores = cosine_similarity(query_vector, vectors)

    ranked_indices = np.argsort(scores)[::-1][:top_k]

    results = []

    for idx in ranked_indices:

        result = {
            "chunk_id": chunk_ids[idx],
            "score": float(scores[idx])
        }

        results.append(result)

    output = {
        "results": results
    }

    return output
