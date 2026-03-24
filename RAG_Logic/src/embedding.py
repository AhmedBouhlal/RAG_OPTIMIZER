from sentence_transformers import SentenceTransformer
import torch


def generate_embeddings(input_dict):

    chunks = input_dict["chunks"]
    config = input_dict["config"]

    model_name = config["embedding_model"]

    # Check for CUDA availability and use it if available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🔥 Using device: {device}")

    model = SentenceTransformer(model_name)
    model = model.to(device)

    texts = [chunk["text"] for chunk in chunks]

    vectors = model.encode(texts, device=device)

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