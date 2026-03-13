import json
import matplotlib.pyplot as plt

with open("results/summary.json", "r", encoding="utf-8") as f:
    summary = json.load(f)

# Extract average scores vs chunk_size
chunk_sizes = [e["config"]["chunk_size"] for e in summary["all_experiments"]]
scores = [e["average_score"] for e in summary["all_experiments"]]

plt.scatter(chunk_sizes, scores)
plt.xlabel("Chunk Size")
plt.ylabel("Average Retrieval Score")
plt.title("Chunk Size vs Retrieval Performance")
plt.show()