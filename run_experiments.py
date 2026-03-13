import multiprocessing as mp
from src.experiment import run_experiment

def run_single_experiment(args):
    exp_counter, cs, ov, tk, model, docs, ground_truths = args
    config = {
        "chunk_size": cs,
        "overlap": ov,
        "top_k": tk,
        "embedding_model": model
    }
    experiment_id = f"exp_{exp_counter:03d}_{model}"
    print(f"Running {experiment_id}: {config}")

    result = run_experiment({
        "experiment_id": experiment_id,
        "config": config,
        "documents": docs,
        "ground_truths": ground_truths
    }, save_path=f"results/{experiment_id}.json")

    print(f"Average retrieval score: {result['average_score']}\n")
    return result


# Prepare grid including embedding models
embedding_models = ["all-MiniLM-L6-v2", "all-MiniLM-L12-v2", "paraphrase-MiniLM-L6-v2"]
chunk_sizes = [100, 200, 300, 400]
overlaps = [20, 50, 80]
top_ks = [1, 3, 5]

tasks = []
exp_counter = 0
for model in embedding_models:
    for cs in chunk_sizes:
        for ov in overlaps:
            for tk in top_ks:
                exp_counter += 1
                tasks.append((exp_counter, cs, ov, tk, model, docs, ground_truths))


# Run in parallel
with mp.Pool(processes=4) as pool:  # adjust number of processes
    pool.map(run_single_experiment, tasks)