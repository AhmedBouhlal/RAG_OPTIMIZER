#!/bin/bash

# ============================
# Full RAG Pipeline Automation
# ============================

# 1️⃣ Activate Python environment
echo "Activating Python virtual environment..."
source venv/bin/activate  # <-- adjust if your venv is elsewhere

# 2️⃣ Load secret OpenAI API key
echo "Loading OpenAI API key from secret_key.json..."
export OPENAI_API_KEY=$(python -c "import json; print(json.load(open('secret_key.json'))['OPENAI_API_KEY'])")

# 3️⃣ Create results and cache folders
mkdir -p results cache

# 4️⃣ Run hyperparameter experiments
echo "Running hyperparameter experiments..."
python run_experiments.py

# 5️⃣ Generate best configuration summary
echo "Generating best config summary..."
python best_config_summary.py

# 6️⃣ Optional: Visualize results
if [ -f visualize_results.py ]; then
    echo "Visualizing experiment results..."
    python visualize_results.py
fi

# 7️⃣ Launch interactive RAG CLI
echo "Launching RAG interactive CLI..."
python rag_cli.py

echo "RAG pipeline finished successfully!"
