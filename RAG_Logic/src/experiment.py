import json
from src.chunking import chunk_documents
from src.embedding import generate_embeddings
from src.vectordb import build_index
from src.retrieval import retrieve_chunks
from src.evaluation import evaluate_retrieval


def run_experiment(input_dict, save_path=None):

    experiment_id = input_dict["experiment_id"]
    config = input_dict["config"]
    documents = input_dict["documents"]
    ground_truths = input_dict["ground_truths"]

    # 1️⃣ Chunking
    chunk_input = {
        "documents": documents,
        "config": {
            "chunk_size": config["chunk_size"],
            "overlap": config["overlap"]
        }
    }
    chunks = chunk_documents(chunk_input)

    # 2️⃣ Embeddings
    embedding_input = {
        "chunks": chunks["chunks"],
        "config": {
            "embedding_model": config.get("embedding_model", "all-MiniLM-L6-v2")
        }
    }
    embeddings = generate_embeddings(embedding_input)

    # 3️⃣ Vector Index
    index_dict = build_index({
        "chunks": chunks["chunks"],
        "embeddings": embeddings["embeddings"]
    })

    # 4️⃣ Retrieval
    retrievals = []
    for gt in ground_truths:
        retrieval = retrieve_chunks({
            "query": gt["query"],
            "config": {
                "embedding_model": config.get("embedding_model", "all-MiniLM-L6-v2"),
                "top_k": config["top_k"]
            },
            "index": index_dict["index"],
            "chunks": index_dict["chunks"]
        })
        retrievals.append(retrieval)

    # 5️⃣ Evaluation
    evaluations = evaluate_retrieval({
        "retrievals": retrievals,
        "ground_truths": ground_truths
    })

    # 6️⃣ Average score
    avg_score = sum(e["retrieval_score"] for e in evaluations["evaluations"]) / max(1, len(evaluations["evaluations"]))

    # 7️⃣ Assemble experiment result
    result = {
        "experiment_id": experiment_id,
        "config": config,
        "evaluations": evaluations["evaluations"],
        "average_score": avg_score
    }

    # 8️⃣ Save JSON
    if save_path:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

    return result
def get_best_config(results_folder="results"):

    import os
    import json

    best_score = -1
    best_config = None
    all_results = []

    for file in os.listdir(results_folder):
        if file.endswith(".json"):
            path = os.path.join(results_folder, file)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                all_results.append(data)
                if data["average_score"] > best_score:
                    best_score = data["average_score"]
                    best_config = data["config"]

    summary = {
        "best_config": best_config,
        "best_score": best_score,
        "all_experiments": all_results
    }

    # Save summary
    with open(os.path.join(results_folder, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary
