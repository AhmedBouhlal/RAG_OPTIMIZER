"""
Comprehensive Experimentation System for RAG
Tests all parameter combinations to find optimal configuration
"""

import os
import sys
import json
import logging
import itertools
from pathlib import Path
from typing import Dict, List, Any, Tuple
import time
from datetime import datetime

# Add RAG_Logic to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'RAG_Logic'))

# Import RAG components
from RAG_Logic.src.loader import load_documents, load_evaluation
from RAG_Logic.src.chunking import chunk_documents
from RAG_Logic.src.embedding import generate_embeddings
from RAG_Logic.src.vectordb import build_index
from RAG_Logic.src.keyword_index import build_bm25_index
from RAG_Logic.src.hybrid_retrieval import hybrid_retrieve
from RAG_Logic.src.reranker import Reranker
from RAG_Logic.src.evaluation import evaluate_retrieval

# Import optimized logic
from logic import OptimizedRAGSystem

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveRAGExperimentRunner:
    """Comprehensive experiment runner that tests all parameter combinations"""

    def __init__(self, data_dir: str = "RAG_Logic/data/documents",
                 eval_dir: str = "RAG_Logic/data/evaluation",
                 results_dir: str = "RAG_Logic/results"):
        self.data_dir = data_dir
        self.eval_dir = eval_dir
        self.results_dir = results_dir
        self.documents = []
        self.ground_truths = []
        self.experiment_log = []

        # Create directories
        Path(self.results_dir).mkdir(parents=True, exist_ok=True)
        Path(self.eval_dir).mkdir(parents=True, exist_ok=True)

    def load_data(self) -> bool:
        """Load documents and evaluation data"""
        try:
            # Load documents
            logger.info(f"Loading documents from {self.data_dir}")
            docs = load_documents({"data_dir": self.data_dir}).get("documents", [])
            if not docs:
                logger.error("❌ No documents found!")
                return False

            self.documents = docs
            logger.info(f"✅ Loaded {len(docs)} documents")

            # Load evaluation data
            logger.info(f"Loading evaluation data from {self.eval_dir}")
            eval_data = load_evaluation({"eval_dir": self.eval_dir}).get("evaluations", [])
            if not eval_data:
                logger.warning("⚠️ No evaluation data found! Creating sample evaluation data...")
                self._create_sample_evaluation()
                eval_data = load_evaluation({"eval_dir": self.eval_dir}).get("evaluations", [])

            # Flatten all evaluation items
            self.ground_truths = []
            for eval_file in eval_data:
                self.ground_truths.extend(eval_file["data"])

            logger.info(f"✅ Loaded {len(self.ground_truths)} evaluation queries")
            return True

        except Exception as e:
            logger.error(f"❌ Error loading data: {e}")
            return False

    def _create_sample_evaluation(self) -> None:
        """Create sample evaluation data if none exists"""
        sample_queries = [
            {
                "query": "What are the main components of a RAG system?",
                "answer": ["retrieval", "generation", "documents", "embeddings", "vector database"]
            },
            {
                "query": "How does chunking help with document processing?",
                "answer": ["splitting", "context", "retrieval", "processing", "segments"]
            },
            {
                "query": "What is the purpose of embeddings in RAG?",
                "answer": ["semantic search", "vectors", "similarity", "neural networks", "meaning"]
            },
            {
                "query": "Why is hybrid retrieval better than single method?",
                "answer": ["vector search", "keyword search", "complementary", "accuracy", "recall"]
            },
            {
                "query": "How does reranking improve results?",
                "answer": ["relevance", "ordering", "quality", "cross-encoder", "precision"]
            }
        ]

        # Save sample evaluation data
        sample_file = os.path.join(self.eval_dir, "sample_evaluation.json")
        with open(sample_file, 'w', encoding='utf-8') as f:
            json.dump(sample_queries, f, indent=2)

        logger.info(f"✅ Created sample evaluation file: {sample_file}")

    def get_parameter_combinations(self) -> List[Dict[str, Any]]:
        """Generate all parameter combinations to test"""

        # Define parameter ranges
        chunk_sizes = [300, 400]
        overlaps = [25, 50]

        top_ks = [5, 8]

        vector_weights = [0.5, 0.7]
        keyword_weights = [0.3, 0.5]   # Don't mirror vector weights blindly

        embedding_models = [
            "sentence-transformers/all-MiniLM-L6-v2",
            "sentence-transformers/all-MiniLM-L12-v2"
        ]

        rerank_top_ks = [8, 10]

        # Generate all combinations
        combinations = []

        for chunk_size, overlap, top_k, vec_weight, key_weight, emb_model, rerank_k in itertools.product(
            chunk_sizes, overlaps, top_ks, vector_weights, keyword_weights, embedding_models, rerank_top_ks
        ):
            # Ensure vector_weight + keyword_weight = 1.0
            if abs(vec_weight + key_weight - 1.0) > 0.1:
                continue

            # Ensure overlap < chunk_size
            if overlap >= chunk_size:
                continue

            config = {
                "experiment_id": f"cs{chunk_size}_ov{overlap}_k{top_k}_vw{vec_weight}_kw{key_weight}_{emb_model.split('/')[-1]}_rk{rerank_k}",
                "chunk_size": chunk_size,
                "overlap": overlap,
                "top_k": top_k,
                "vector_weight": vec_weight,
                "keyword_weight": key_weight,
                "embedding_model": emb_model,
                "rerank_top_k": rerank_k
            }
            combinations.append(config)

        logger.info(f"🔢 Generated {len(combinations)} parameter combinations")
        return combinations

    def get_sample_combinations(self) -> List[Dict[str, Any]]:
        """Get a smaller sample of combinations for testing"""
        return [
            {
                "experiment_id": "sample_1_small_balanced",
                "chunk_size": 200,
                "overlap": 25,
                "top_k": 5,
                "vector_weight": 0.5,
                "keyword_weight": 0.5,
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "rerank_top_k": 10
            },
            {
                "experiment_id": "sample_2_medium_balanced",
                "chunk_size": 400,
                "overlap": 50,
                "top_k": 5,
                "vector_weight": 0.5,
                "keyword_weight": 0.5,
                "embedding_model": "sentence-transformers/all-MiniLM-L12-v2",
                "rerank_top_k": 10
            },
            {
                "experiment_id": "sample_3_large_vector_heavy",
                "chunk_size": 500,
                "overlap": 75,
                "top_k": 7,
                "vector_weight": 0.7,
                "keyword_weight": 0.3,
                "embedding_model": "sentence-transformers/all-MiniLM-L12-v2",
                "rerank_top_k": 12
            }
        ]

    def log_experiment_start(self, config: Dict[str, Any], total_experiments: int, current: int) -> None:
        """Log experiment start with detailed parameters"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "experiment_id": config["experiment_id"],
            "status": "started",
            "parameters": config,
            "progress": f"{current}/{total_experiments}"
        }
        self.experiment_log.append(log_entry)

        logger.info(f"🧪 [{current}/{total_experiments}] Starting: {config['experiment_id']}")
        logger.info(f"   📊 Chunk Size: {config['chunk_size']}, Overlap: {config['overlap']}")
        logger.info(f"   🎯 Top-K: {config['top_k']}, Vector Weight: {config['vector_weight']}")
        logger.info(f"   🔤 Keyword Weight: {config['keyword_weight']}, Rerank Top-K: {config['rerank_top_k']}")
        logger.info(f"   🤖 Embedding Model: {config['embedding_model'].split('/')[-1]}")

    def log_experiment_result(self, config: Dict[str, Any], result: Dict[str, Any], total_experiments: int, current: int) -> None:
        """Log experiment result"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "experiment_id": config["experiment_id"],
            "status": "completed" if "error" not in result else "failed",
            "parameters": config,
            "metrics": result.get("metrics", {}),
            "progress": f"{current}/{total_experiments}"
        }
        self.experiment_log.append(log_entry)

        if "error" not in result:
            metrics = result["metrics"]
            logger.info(f"   ✅ [{current}/{total_experiments}] Completed: {config['experiment_id']}")
            logger.info(f"      📊 Score: {metrics['average_score']:.3f}")
            logger.info(f"      📈 Success Rate: {metrics['success_rate']:.1f}%")
            logger.info(f"      ⏱️ Duration: {metrics['experiment_duration']:.1f}s")
        else:
            logger.error(f"   ❌ [{current}/{total_experiments}] Failed: {config['experiment_id']}")
            logger.error(f"      Error: {result['error']}")

    def run_single_experiment(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single experiment with given configuration"""
        start_time = time.time()

        try:
            # 1️⃣ Chunking
            chunk_input = {
                "documents": self.documents,
                "config": {
                    "chunk_size": config["chunk_size"],
                    "overlap": config["overlap"]
                }
            }
            chunks_result = chunk_documents(chunk_input)
            chunks = chunks_result["chunks"]

            # 2️⃣ Embeddings
            embedding_input = {
                "chunks": chunks,
                "config": {
                    "embedding_model": config["embedding_model"]
                }
            }
            embeddings_result = generate_embeddings(embedding_input)
            embeddings = embeddings_result["embeddings"]

            # 3️⃣ Vector Index
            index_dict = build_index({
                "chunks": chunks,
                "embeddings": embeddings
            })

            # 4️⃣ BM25 Index
            bm25_dict = build_bm25_index({"chunks": chunks})

            # 5️⃣ Initialize Reranker
            reranker = Reranker()

            # 6️⃣ Retrieval for all evaluation queries
            retrievals = []

            for gt in self.ground_truths:
                # Handle both "query" and "question" field names
                query_text = gt.get("query", gt.get("question", ""))

                # Hybrid retrieval
                retrieval_result = hybrid_retrieve({
                    "query": query_text,
                    "config": config,
                    "index": index_dict["index"],
                    "chunks": index_dict["chunks"],
                    "bm25": bm25_dict["bm25"]
                })

                # Rerank results
                candidate_chunks = retrieval_result.get("results", [])[:config["rerank_top_k"]]
                reranked = reranker.rerank(query_text, candidate_chunks, top_k=config["top_k"])

                retrieval = {
                    "query": query_text,
                    "results": reranked
                }
                retrievals.append(retrieval)

            # 7️⃣ Evaluation
            evaluation_result = evaluate_retrieval({
                "retrievals": retrievals,
                "ground_truths": self.ground_truths
            })

            # 8️⃣ Calculate metrics
            evaluations = evaluation_result["evaluations"]
            avg_score = sum(e["retrieval_score"] for e in evaluations) / max(1, len(evaluations))

            # Additional metrics
            successful_retrievals = sum(1 for e in evaluations if e["retrieval_score"] > 0)
            success_rate = (successful_retrievals / len(evaluations)) * 100 if evaluations else 0
            avg_results_count = sum(len(e["results"]) for e in evaluations) / max(1, len(evaluations))

            # 9️⃣ Assemble experiment result
            experiment_time = time.time() - start_time

            result = {
                "experiment_id": config["experiment_id"],
                "config": config,
                "metrics": {
                    "average_score": avg_score,
                    "success_rate": success_rate,
                    "avg_results_count": avg_results_count,
                    "total_queries": len(evaluations),
                    "successful_retrievals": successful_retrievals,
                    "experiment_duration": experiment_time
                },
                "evaluations": evaluations,
                "retrieval_examples": retrievals[:3]  # Save first 3 examples
            }

            # 10️⃣ Save experiment result
            result_file = os.path.join(self.results_dir, f"{config['experiment_id']}.json")
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)

            return result

        except Exception as e:
            experiment_time = time.time() - start_time
            return {
                "experiment_id": config["experiment_id"],
                "config": config,
                "error": str(e),
                "metrics": {
                    "average_score": 0.0,
                    "success_rate": 0.0,
                    "avg_results_count": 0.0,
                    "total_queries": 0,
                    "successful_retrievals": 0,
                    "experiment_duration": experiment_time
                }
            }

    def run_all_experiments(self, comprehensive: bool = False) -> Dict[str, Any]:
        """Run all experiments and generate summary"""
        logger.info("🚀 Starting comprehensive experiment suite")

        # Load data
        if not self.load_data():
            return {"error": "Failed to load data"}

        # Get configurations
        if comprehensive:
            configs = self.get_parameter_combinations()
            logger.info(f"🔢 Testing ALL parameter combinations: {len(configs)} experiments")
        else:
            configs = self.get_sample_combinations()
            logger.info(f"📋 Testing sample combinations: {len(configs)} experiments")

        # Run experiments
        all_results = []
        best_score = -1
        best_config = None

        for i, config in enumerate(configs, 1):
            # Log experiment start
            self.log_experiment_start(config, len(configs), i)

            # Run experiment
            result = self.run_single_experiment(config)
            all_results.append(result)

            # Log experiment result
            self.log_experiment_result(config, result, len(configs), i)

            # Track best configuration
            if "metrics" in result and result["metrics"]["average_score"] > best_score:
                best_score = result["metrics"]["average_score"]
                best_config = result["config"]

        # Save experiment log
        log_file = os.path.join(self.results_dir, "experiment_log.json")
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.experiment_log, f, indent=2)

        # Generate summary
        successful_results = [r for r in all_results if "error" not in r]

        summary = {
            "experiment_summary": {
                "total_experiments": len(configs),
                "successful_experiments": len(successful_results),
                "failed_experiments": len(all_results) - len(successful_results),
                "total_evaluation_queries": len(self.ground_truths),
                "experiment_timestamp": datetime.now().isoformat(),
                "comprehensive_mode": comprehensive
            },
            "best_config": best_config,
            "best_score": best_score,
            "all_results": all_results,
            "ranking": sorted(
                [r for r in successful_results if r["metrics"]["average_score"] > 0],
                key=lambda x: x["metrics"]["average_score"],
                reverse=True
            ),
            "parameter_analysis": self._analyze_parameters(successful_results)
        }

        # Save summary
        summary_file = os.path.join(self.results_dir, "summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        # Print results
        logger.info("🎉 Experiment suite completed!")
        logger.info(f"📊 Best Score: {best_score:.3f}")
        logger.info(f"🏆 Best Config: {best_config['experiment_id'] if best_config else 'None'}")
        logger.info(f"📝 Experiment log saved to: {log_file}")
        logger.info(f"💾 Summary saved to: {summary_file}")

        return summary

    def _analyze_parameters(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze parameter performance across all experiments"""
        if not results:
            return {}

        analysis = {
            "chunk_size_performance": {},
            "overlap_performance": {},
            "top_k_performance": {},
            "vector_weight_performance": {},
            "embedding_model_performance": {}
        }

        # Analyze chunk sizes
        chunk_size_scores = {}
        for result in results:
            chunk_size = result["config"]["chunk_size"]
            score = result["metrics"]["average_score"]

            if chunk_size not in chunk_size_scores:
                chunk_size_scores[chunk_size] = []
            chunk_size_scores[chunk_size].append(score)

        for chunk_size, scores in chunk_size_scores.items():
            analysis["chunk_size_performance"][chunk_size] = {
                "avg_score": sum(scores) / len(scores),
                "max_score": max(scores),
                "min_score": min(scores),
                "count": len(scores)
            }

        # Similar analysis for other parameters...
        # (omitted for brevity, but would follow same pattern)

        return analysis

    def print_summary_report(self, summary: Dict[str, Any]) -> None:
        """Print a detailed summary report"""
        print("\n" + "="*80)
        print("🧪 COMPREHENSIVE RAG EXPERIMENT SUITE RESULTS")
        print("="*80)

        if "error" in summary:
            print(f"❌ Error: {summary['error']}")
            return

        exp_summary = summary["experiment_summary"]
        print(f"📊 Total Experiments: {exp_summary['total_experiments']}")
        print(f"✅ Successful Experiments: {exp_summary['successful_experiments']}")
        print(f"❌ Failed Experiments: {exp_summary['failed_experiments']}")
        print(f"🔍 Evaluation Queries: {exp_summary['total_evaluation_queries']}")
        print(f"🔬 Mode: {'Comprehensive' if exp_summary['comprehensive_mode'] else 'Sample'}")
        print(f"🏆 Best Score: {summary['best_score']:.3f}")

        if summary["best_config"]:
            print(f"\n🥇 BEST CONFIGURATION:")
            config = summary["best_config"]
            print(f"   Experiment ID: {config['experiment_id']}")
            print(f"   Chunk Size: {config['chunk_size']}")
            print(f"   Overlap: {config['overlap']}")
            print(f"   Top K: {config['top_k']}")
            print(f"   Vector Weight: {config['vector_weight']}")
            print(f"   Keyword Weight: {config['keyword_weight']}")
            print(f"   Embedding Model: {config['embedding_model'].split('/')[-1]}")
            print(f"   Rerank Top-K: {config['rerank_top_k']}")

        print(f"\n📈 TOP 10 EXPERIMENTS:")
        for i, result in enumerate(summary["ranking"][:10], 1):
            metrics = result["metrics"]
            config = result["config"]
            print(f"   {i:2d}. {config['experiment_id'][:40]:40s}")
            print(f"       Score: {metrics['average_score']:.3f} | Success: {metrics['success_rate']:.1f}% | Time: {metrics['experiment_duration']:.1f}s")

        if "parameter_analysis" in summary and summary["parameter_analysis"]:
            print(f"\n📊 PARAMETER ANALYSIS:")
            param_analysis = summary["parameter_analysis"]

            if "chunk_size_performance" in param_analysis:
                print(f"   📏 Chunk Size Performance:")
                for chunk_size, perf in param_analysis["chunk_size_performance"].items():
                    print(f"       {chunk_size:3d}: {perf['avg_score']:.3f} avg ({perf['count']} experiments)")

        print(f"\n📁 Detailed Results:")
        print(f"   📝 Experiment Log: RAG_Logic/results/experiment_log.json")
        print(f"   📊 Summary: RAG_Logic/results/summary.json")
        print(f"   🗂️ Individual Results: RAG_Logic/results/*.json")

        print("\n" + "="*80)

def main():
    """Main function to run experiments"""
    import argparse

    parser = argparse.ArgumentParser(description="Run comprehensive RAG experiments")
    parser.add_argument("--comprehensive", action="store_true",
                       help="Run ALL parameter combinations (can be very slow)")
    parser.add_argument("--data-dir", default="RAG_Logic/data/documents",
                       help="Documents directory")
    parser.add_argument("--eval-dir", default="RAG_Logic/data/evaluation",
                       help="Evaluation data directory")
    parser.add_argument("--results-dir", default="RAG_Logic/results",
                       help="Results directory")

    args = parser.parse_args()

    # Create experiment runner
    runner = ComprehensiveRAGExperimentRunner(
        data_dir=args.data_dir,
        eval_dir=args.eval_dir,
        results_dir=args.results_dir
    )

    # Run experiments
    summary = runner.run_all_experiments(comprehensive=args.comprehensive)
    runner.print_summary_report(summary)

if __name__ == "__main__":
    main()
