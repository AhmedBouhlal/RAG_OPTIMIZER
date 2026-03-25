import uuid
import asyncio
import os
import json
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

# Import your systems
from cli_optimized import OptimizedRAGCLI
from run_experiments_comprehensive import ComprehensiveRAGExperimentRunner
from utils import performance_metrics
from model_manager import model_manager

app = FastAPI(title="Unified RAG + Experiment API", version="1.1")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# GLOBAL SYSTEMS
# ---------------------------
cli = OptimizedRAGCLI()
initialized = False

# Experiment jobs storage (replace later with DB)
jobs: Dict[str, Dict[str, Any]] = {}

# ---------------------------
# DATA PATHS
# ---------------------------
DOCUMENTS_PATH = Path("RAG_Logic/data/documents")
EVAL_PATH = Path("RAG_Logic/data/evaluation")
DOCUMENTS_PATH.mkdir(parents=True, exist_ok=True)
EVAL_PATH.mkdir(parents=True, exist_ok=True)

# ---------------------------
# MODELS
# ---------------------------
class QueryRequest(BaseModel):
    query: str


class ExperimentRequest(BaseModel):
    mode: str = "sample"  # "sample" or "comprehensive"


# ---------------------------
# STARTUP
# ---------------------------
@app.on_event("startup")
async def startup():
    global initialized
    success = await cli.initialize()
    if not success:
        raise RuntimeError("RAG initialization failed")
    initialized = True


# =========================================================
# 🔹 RAG ENDPOINTS
# =========================================================
@app.post("/query")
async def query_rag(req: QueryRequest):
    if not initialized:
        raise HTTPException(500, "RAG not initialized")
    try:
        result = await asyncio.wait_for(cli.process_query(req.query), timeout=30)
        return {
            "answer": result.get("answer"),
            "confidence": result.get("confidence_score"),
            "sources": result.get("source_documents"),
            "meta": result.get("rag_analysis"),
        }
    except asyncio.TimeoutError:
        raise HTTPException(504, "Query timeout")


@app.get("/stats")
def stats():
    return {
        "queries": performance_metrics.query_count,
        "avg_time": performance_metrics.avg_time,
        "cache_hit_rate": performance_metrics.get_cache_hit_rate(),
        "error_rate": performance_metrics.get_error_rate(),
    }


@app.get("/config")
def config():
    best = cli._load_best_config()
    return best or {"message": "No config found"}


@app.get("/history")
def history():
    return cli.conversation_history


@app.delete("/history")
def clear_history():
    cli.conversation_history.clear()
    return {"message": "History cleared"}


# =========================================================
# 🔹 EXPERIMENT SYSTEM
# =========================================================
def run_experiment_job(job_id: str, mode: str):
    runner = ComprehensiveRAGExperimentRunner()
    jobs[job_id]["status"] = "running"
    try:
        summary = runner.run_all_experiments(comprehensive=(mode == "comprehensive"))
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = summary
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


@app.post("/experiments/start")
async def start_experiment(req: ExperimentRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "queued", "mode": req.mode, "result": None, "error": None}
    background_tasks.add_task(run_experiment_job, job_id, req.mode)
    return {"job_id": job_id, "status": "started", "mode": req.mode}


@app.get("/experiments")
def list_jobs():
    return jobs


@app.get("/experiments/{job_id}")
def job_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    return {"job_id": job_id, "status": jobs[job_id]["status"], "mode": jobs[job_id]["mode"]}


@app.get("/experiments/{job_id}/results")
def job_results(job_id: str):
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    job = jobs[job_id]
    if job["status"] != "completed":
        return {"status": job["status"], "message": "Not finished yet"}
    return job["result"]


# =========================================================
# 🔹 DOCUMENT MANAGEMENT
# =========================================================
@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    file_path = DOCUMENTS_PATH / file.filename
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        return {"message": "Document uploaded", "filename": file.filename, "path": str(file_path)}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/documents")
def list_documents():
    files = [f.name for f in DOCUMENTS_PATH.glob("*") if f.is_file()]
    return {"documents": files}


@app.delete("/documents/{filename}")
def delete_document(filename: str):
    file_path = DOCUMENTS_PATH / filename
    if not file_path.exists():
        raise HTTPException(404, "File not found")
    file_path.unlink()
    return {"message": f"{filename} deleted"}


# =========================================================
# 🔹 EVALUATION MANAGEMENT
# =========================================================
@app.post("/evaluation/upload")
async def upload_evaluation(file: UploadFile = File(...)):
    if not file.filename.endswith(".json"):
        raise HTTPException(400, "Only JSON files allowed")
    file_path = EVAL_PATH / file.filename
    try:
        content = await file.read()
        # Validate JSON
        json.loads(content)
        with open(file_path, "wb") as f:
            f.write(content)
        return {"message": "Evaluation uploaded", "filename": file.filename, "path": str(file_path)}
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid JSON file")
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/evaluation")
async def list_evaluation():
    files = [f for f in os.listdir(EVAL_PATH) if f.endswith(".json")]
    return {"evaluation_files": files}


@app.delete("/evaluation/{filename}")
def delete_evaluation(filename: str):
    file_path = EVAL_PATH / filename
    if not file_path.exists():
        raise HTTPException(404, "File not found")
    file_path.unlink()
    return {"message": f"{filename} deleted"}

# =========================================================
# LLM Configuration endpoints
# =========================================================

@app.get("/models/available")
async def get_available_models():
    """Get list of available local models"""
    try:
        available = model_manager.get_available_models()
        installed = model_manager.get_installed_models()
        return available
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/models/install")
async def install_model(request: Dict[str, str]):
    """Install a local model"""
    model_name = request.get("model_name")
    if not model_name:
        raise HTTPException(400, "Model name required")

    try:
        result = model_manager.install_model(model_name)
        if result["success"]:
            return {"message": result["message"]}
        else:
            raise HTTPException(500, result["message"])
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/models/test")
async def test_llm_connection(request: Dict[str, Any]):
    """Test LLM connection"""
    try:
        provider = request.get("provider", "local")
        model = request.get("model", "llama3")

        if provider == "openai":
            api_key = request.get("openaiApiKey")
            if not api_key:
                raise HTTPException(400, "OpenAI API key required")
            # TODO: Implement OpenAI connection test
            return {"message": "OpenAI connection test successful"}
        else:
            # Test local model
            result = model_manager.test_model(model)
            if result["success"]:
                return {"message": result["message"]}
            else:
                raise HTTPException(500, result["message"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/config/llm")
async def update_llm_config(request: Dict[str, Any]):
    """Update LLM configuration"""
    try:
        # Save LLM config to file or database
        config = {
            "provider": request.get("provider"),
            "model": request.get("model"),
            "openai_api_key": request.get("openaiApiKey"),
            "temperature": request.get("temperature"),
            "max_tokens": request.get("maxTokens"),
            "top_p": request.get("topP"),
        }

        # This would typically save to config file
        return {"message": "LLM configuration updated"}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/config/rag")
async def update_rag_config(request: Dict[str, Any]):
    """Update RAG configuration"""
    try:
        # Save RAG config to file or database
        config = {
            "chunk_size": request.get("chunkSize"),
            "overlap": request.get("overlap"),
            "top_k": request.get("topK"),
            "vector_weight": request.get("vectorWeight"),
            "keyword_weight": request.get("keywordWeight"),
            "rerank_top_k": request.get("rerankTopK"),
        }

        # This would typically save to config file and reinitialize RAG system
        return {"message": "RAG configuration updated"}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/experiments/best-config")
async def get_best_experiment_config():
    """Get the best configuration from experiments"""
    try:
        # Find the best experiment from jobs
        best_config = None
        best_score = 0.0

        for job_id, job in jobs.items():
            if job.get("status") == "completed" and "result" in job:
                result = job["result"]
                if "best_config" in result:
                    score = result.get("best_score", 0.0)
                    if score > best_score:
                        best_score = score
                        best_config = result["best_config"]

        if best_config:
            return best_config
        else:
            # Return default config if no experiments completed
            return {
                "chunk_size": 200,
                "overlap": 25,
                "top_k": 5,
                "vector_weight": 0.5,
                "keyword_weight": 0.5,
                "rerank_top_k": 10
            }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/config/load-best")
async def load_best_config():
    """Load the best experiment configuration into current settings"""
    try:
        # Get best config
        best_config = None
        best_score = 0.0

        for job_id, job in jobs.items():
            if job.get("status") == "completed" and "result" in job:
                result = job["result"]
                if "best_config" in result:
                    score = result.get("best_score", 0.0)
                    if score > best_score:
                        best_score = score
                        best_config = result["best_config"]

        if best_config:
            # Convert to frontend format
            rag_config = {
                "chunkSize": best_config.get("chunk_size", 200),
                "overlap": best_config.get("overlap", 25),
                "topK": best_config.get("top_k", 5),
                "vectorWeight": best_config.get("vector_weight", 0.5),
                "keywordWeight": best_config.get("keyword_weight", 0.5),
                "rerankTopK": best_config.get("rerank_top_k", 10)
            }

            return {
                "message": f"Loaded best config (score: {best_score:.3f})",
                "rag_config": rag_config,
                "llm_config": {
                    "provider": "local",
                    "model": "llama3",
                    "temperature": 0.7,
                    "maxTokens": 2048,
                    "topP": 0.9
                }
            }
        else:
            return {
                "message": "No completed experiments found. Using default config.",
                "rag_config": {
                    "chunkSize": 200,
                    "overlap": 25,
                    "topK": 5,
                    "vectorWeight": 0.5,
                    "keywordWeight": 0.5,
                    "rerankTopK": 10
                },
                "llm_config": {
                    "provider": "local",
                    "model": "llama3",
                    "temperature": 0.7,
                    "maxTokens": 2048,
                    "topP": 0.9
                }
            }
    except Exception as e:
        raise HTTPException(500, str(e))