# best_config_summary.py

from src.experiment import get_best_config

# Folder where experiment JSON files are saved
results_folder = "results"

# Load summary and best config
summary = get_best_config(results_folder)

print("===== Best RAG Configuration =====")
print(f"Best configuration: {summary['best_config']}")
print(f"Best score: {summary['best_score']}\n")

# Optionally, you can explore all experiments
print("All experiment results:")
for exp in summary["all_experiments"]:
    print(f"{exp['experiment_id']} → Avg score: {exp['average_score']}")
