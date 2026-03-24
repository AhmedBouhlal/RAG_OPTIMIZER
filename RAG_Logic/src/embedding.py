from sentence_transformers import SentenceTransformer


def generate_embeddings(input_dict):

    chunks = input_dict["chunks"]
    config = input_dict["config"]

    model_name = config["embedding_model"]

    model = SentenceTransformer(model_name)

    texts = [chunk["text"] for chunk in chunks]

    vectors = model.encode(texts)

    embeddings = []

    for chunk, vector in zip(chunks, vectors):

        item = {
            "chunk_id": chunk["chunk_id"],
            "doc_id": chunk["doc_id"],
            "vector": vector.tolist()
        }

        embeddings.append(item)

    output = {
        "embeddings": embeddings
    }

    return output