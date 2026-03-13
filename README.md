```markdown
# RAG Hyperparameter Optimization System

A **Research-Ready Retrieval-Augmented Generation (RAG) system** with **automatic hyperparameter optimization**, multi-document support, and interactive query capability.  

This project allows you to:

- Automatically search for the best RAG hyperparameters (`chunk_size`, `chunk_overlap`, `top_k`, `embedding_model`)  
- Build vector indexes and embeddings from multiple documents  
- Retrieve relevant chunks for user queries  
- Generate answers using GPT (OpenAI API or local LLMs)  
- Visualize experiment results  
- Run everything in **parallel and fully automated** via Bash  

---

## **Table of Contents**

1. [Project Structure](#project-structure)  
2. [Setup Instructions](#setup-instructions)  
3. [Documents & Evaluation Dataset](#documents--evaluation-dataset)  
4. [Running Experiments](#running-experiments)  
5. [Generating Best Config Summary](#generating-best-config-summary)  
6. [Interactive RAG CLI](#interactive-rag-cli)  
7. [Visualization](#visualization)  
8. [API Key Management](#api-key-management)  
9. [Bash Automation Script](#bash-automation-script)  
10. [File Descriptions](#file-descriptions)  
11. [Notes & Tips](#notes--tips)  

---

## **Project Structure**


rag_optimizer/
├── best_config_summary.py      # Generate best hyperparameter config JSON
├── data/
│   ├── documents/             # Source documents (.txt)
│   └── evaluation/            # Question/answer evaluation dataset
├── rag_cli.py                 # Interactive RAG CLI for queries
├── run_experiments.py         # Runs hyperparameter experiments in parallel
├── secret_key.json            # OpenAI API key (ignored in Git)
├── src/
│   ├── chunking.py            # Splits documents into chunks
│   ├── embedding.py           # Generates embeddings (sentence-transformers)
│   ├── evaluation.py          # Evaluates retrieval results
│   ├── experiment.py          # Runs a single experiment
│   ├── loader.py              # Loads documents
│   ├── retrieval.py           # Retrieves top-k chunks from index
│   └── vectordb.py            # Builds vector index
├── visualize_results.py       # Plots experiment results
├── run_all.sh                 # Full pipeline automation
├── README.md
└── requirements.txt

````

---

## **Setup Instructions**

1. **Clone the repository**:

```bash
git clone <your_repo_url>
cd rag_optimizer
````

2. **Create a Python virtual environment**:

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

3. **Install dependencies**:

```bash
pip install -r requirements.txt
# Requirements include:
# - openai
# - sentence-transformers
# - transformers
# - torch
# - matplotlib
```

4. **Prepare documents**:

Place `.txt` files in `data/documents/`. Each file will be assigned a `doc_id`.

5. **Prepare evaluation dataset**:

* Store question/answer pairs in `data/evaluation/` (JSON or CSV).
* Used to calculate retrieval scores during experiments.

---

## **Documents & Evaluation Dataset**

* **Document Format**:

```json
{
  "doc_id": "doc_001",
  "file_name": "alice.txt",
  "text": "Alice saw the White Rabbit..."
}
```

* **Chunk Format**:

```json
{
  "chunk_id": "doc_01_chunk_05",
  "doc_id": "doc_01",
  "text": "...",
  "start_word": 500,
  "end_word": 800
}
```

* **Retrieval Result Format**:

```json
{
  "query": "Who follows Alice?",
  "results": [
    {
      "chunk_id": "doc_01_chunk_05",
      "score": 0.91,
      "text": "Alice saw the White Rabbit..."
    }
  ]
}
```

---

## **Running Experiments**

* `run_experiments.py` automatically tests multiple configurations:

```bash
python run_experiments.py
```

* Hyperparameters tested:

```python
chunk_sizes = [100, 200, 300, 400]
overlaps = [20, 50, 80]
top_ks = [1, 3, 5]
embedding_models = ["all-MiniLM-L6-v2","all-MiniLM-L12-v2","paraphrase-MiniLM-L6-v2"]
```

* Results saved as JSON files in `results/`:

```
results/exp_001_all-MiniLM-L6-v2.json
results/exp_002_all-MiniLM-L12-v2.json
...
```

---

## **Generating Best Config Summary**

* Run `best_config_summary.py`:

```bash
python best_config_summary.py
```

* Generates `results/summary.json`:

```json
{
  "best_config": {
    "chunk_size": 300,
    "overlap": 50,
    "top_k": 3,
    "embedding_model": "all-MiniLM-L6-v2"
  },
  "best_score": 0.92
}
```

---

## **Interactive RAG CLI**

* Launch CLI:

```bash
python rag_cli.py
```

* Type queries:

```
Query: Who follows Alice?
Generated Answer: The White Rabbit follows Alice down the rabbit hole.
Query: exit
```

* Features:

  * Retrieves top-k chunks using best config
  * Sends chunks to GPT for answer generation
  * Fully modular, dictionary/JSON-based

---

## **Visualization**

* Run `visualize_results.py` to plot experiment results:

```bash
python visualize_results.py
```

* Visualizations:

  * Chunk size vs retrieval score
  * Overlap vs retrieval score
  * Heatmaps for hyperparameter interactions

---

## **API Key Management**

* Store OpenAI API key in `secret_key.json`:

```json
{
  "OPENAI_API_KEY": "sk-xxxxxxxxxxxxxxxxxxxx"
}
```

* **Never commit** this file to Git!
* Loaded automatically in scripts and Bash automation.

---

## **Bash Automation Script**

* Run **full pipeline** with one command:

```bash
chmod +x run_all.sh
./run_all.sh
```

* Steps performed:

  1. Activate Python environment
  2. Load OpenAI API key
  3. Run experiments in parallel
  4. Generate best config summary
  5. Optionally visualize results
  6. Launch interactive RAG CLI

---

## **File Descriptions**

| File                     | Purpose                                                     |
| ------------------------ | ----------------------------------------------------------- |
| `src/loader.py`          | Load documents into structured dictionaries                 |
| `src/chunking.py`        | Split documents into chunks with `chunk_size` and `overlap` |
| `src/embedding.py`       | Generate embeddings for chunks                              |
| `src/vectordb.py`        | Build vector index for retrieval                            |
| `src/retrieval.py`       | Retrieve top-k chunks for queries                           |
| `src/evaluation.py`      | Score retrieval using evaluation dataset                    |
| `src/experiment.py`      | Run single experiment and return JSON results               |
| `run_experiments.py`     | Runs all hyperparameter experiments in parallel             |
| `best_config_summary.py` | Reads all experiment JSONs and finds the best config        |
| `rag_cli.py`             | Interactive RAG query interface                             |
| `visualize_results.py`   | Plots experiment results                                    |
| `secret_key.json`        | Stores OpenAI API key (ignored in Git)                      |

---

## **Notes & Tips**

* Use **`cache/`** to store embeddings and speed up repeated runs
* Adjust **`processes`** in experiments depending on CPU cores
* Truncate long chunks for GPT to avoid token limits
* Keep `data/evaluation/` updated for accurate experiment scoring
* Modular dictionary/JSON design allows easy replacement of GPT with **local LLMs**

---

> By following this guide, you can run the **entire RAG system from scratch**, explore hyperparameter space, and interactively query your documents using GPT.

```

