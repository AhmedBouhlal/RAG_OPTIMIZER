# run_experiments.py
import multiprocessing as mp
from src.experiment import run_experiment
from src.loader import load_documents, load_evaluation
import os
from huggingface_hub import login
import json

def run_single_experiment(args):
    exp_counter, cs, ov, tk, model, docs, ground_truths, eval_file = args

    config = {
        "chunk_size": cs,
        "overlap": ov,
        "top_k": tk,
        "embedding_model": model
    }
    experiment_id = f"exp_{exp_counter:03d}_{model}_{eval_file}"
    print(f"\nRunning {experiment_id}: {config}")


    # Make sure the results folder exists
    os.makedirs("results", exist_ok=True)
    
    try:
        result = run_experiment({
            "experiment_id": experiment_id,
            "config": config,
            "documents": docs,
            "ground_truths": ground_truths
        }, save_path=f"results/{experiment_id}.json")

        print(f"Average retrieval score: {result['average_score']}\n")
        return result

    except Exception as e:
        print(f"Experiment {experiment_id} failed with error: {e}")
        return None


if __name__ == "__main__":

    with open("hf_token.json", "r") as f:
        token_data = json.load(f)

    hf_token = token_data["HF_TOKEN"]

    # Login to Hugging Face
    login(token=hf_token)
    # -----------------------------
    # Prepare hyperparameter grid
    # -----------------------------
    embedding_models = ["all-MiniLM-L6-v2", "all-MiniLM-L12-v2", "paraphrase-MiniLM-L6-v2"]
    chunk_sizes = [100, 200, 300, 400]
    overlaps = [20, 50, 80]
    top_ks = [1, 3, 5]

    # -----------------------------
    # Load documents
    # -----------------------------
    docs = load_documents({"data_dir": "data/documents"})["documents"]

    # -----------------------------
    # Load all evaluation datasets
    # -----------------------------
    evals = load_evaluation({"eval_dir": "data/evaluation"})["evaluations"]

    # -----------------------------
    # Prepare tasks for multiprocessing
    # -----------------------------
    tasks = []
    exp_counter = 0
    for eval_data in evals:
        ground_truths = eval_data["data"]
        eval_file = eval_data["file_name"].replace(".json", "")
        for model in embedding_models:
            for cs in chunk_sizes:
                for ov in overlaps:
                    for tk in top_ks:
                        exp_counter += 1
                        tasks.append((exp_counter, cs, ov, tk, model, docs, ground_truths, eval_file))

    # -----------------------------
    # Run experiments in parallel
    # -----------------------------
    with mp.Pool(processes=4) as pool:  # Adjust to your CPU cores
        pool.map(run_single_experiment, tasks)