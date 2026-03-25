import uuid
import asyncio
import os
import json
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any

# Import your systems
from your_cli_file import OptimizedRAGCLI
from your_experiment_file import ComprehensiveRAGExperimentRunner
from utils import performance_metrics

app = FastAPI(title="Unified RAG + Experiment API", version="1.1")

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
def list_evaluation_files():
    files = [f.name for f in EVAL_PATH.glob("*.json") if f.is_file()]
    return {"evaluation_files": files}


@app.delete("/evaluation/{filename}")
def delete_evaluation(filename: str):
    file_path = EVAL_PATH / filename
    if not file_path.exists():
        raise HTTPException(404, "File not found")
    file_path.unlink()
    return {"message": f"{filename} deleted"}