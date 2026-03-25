"""
Simplified Optimized Universal RAG System
Clean version without complex production features
"""

import sys
import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import numpy as np
from datetime import datetime

# Add RAG_Logic to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'RAG_Logic'))

# Import simplified components
from config import config, setup_logging
from utils import (
    error_handler, async_error_handler, cache_result,
    SimpleCache, BatchProcessor, performance_metrics,
    RAGError, EmbeddingError, RetrievalError, GenerationError
)

# RAG imports
from RAG_Logic.src.loader import load_documents
from RAG_Logic.src.chunking import chunk_documents
from RAG_Logic.src.vectordb import build_index, cosine_similarity, search_index
from RAG_Logic.src.keyword_index import build_bm25_index, bm25_search
from RAG_Logic.src.rrf import reciprocal_rank_fusion
from RAG_Logic.src.reranker import Reranker

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class OptimizedEmbeddingService:
    """Simplified embedding service with caching"""

    def __init__(self, model_name: str, cache_manager: SimpleCache):
        self.model_name = model_name
        self.cache_manager = cache_manager
        self._model = None
        self.batch_processor = BatchProcessor(
            batch_size=config.embedding_batch_size,
            max_workers=4
        )

    def _get_model(self):
        """Lazy load embedding model"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                import torch

                self._model = SentenceTransformer(self.model_name)

                # Move to CUDA if available
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self._model = self._model.to(device)

                logger.info(f"Loaded embedding model: {self.model_name} on {device}")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise EmbeddingError(f"Could not load model {self.model_name}: {e}")
        return self._model

    @error_handler
    def _encode_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Encode a batch of texts"""
        import torch

        model = self._get_model()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        return model.encode(texts, batch_size=len(texts), device=device)

    @cache_result(SimpleCache(config.cache_dir), ttl=config.cache_ttl)
    async def generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate embeddings with caching"""
        if not chunks:
            return []

        # Check cache first
        cached_results = []
        uncached_chunks = []

        for chunk in chunks:
            cache_key = f"embedding:{chunk['text'][:100]}"
            cached = await self.cache_manager.get(cache_key)

            if cached is not None:
                cached_results.append({
                    "chunk_id": chunk["chunk_id"],
                    "doc_id": chunk["doc_id"],
                    "vector": cached,
                    "_from_cache": True
                })
            else:
                uncached_chunks.append((chunk, cache_key))

        if not uncached_chunks:
            logger.info(f"All {len(chunks)} embeddings found in cache")
            return cached_results

        # Process uncached chunks
        logger.info(f"Generating embeddings for {len(uncached_chunks)} chunks")

        texts = [chunk["text"] for chunk, _ in uncached_chunks]
        embeddings = self.batch_processor.process_batches(texts, self._encode_batch)

        # Create results and cache them
        new_results = []
        for (chunk, cache_key), vector in zip(uncached_chunks, embeddings):
            if vector is not None:
                embedding_data = {
                    "chunk_id": chunk["chunk_id"],
                    "doc_id": chunk["doc_id"],
                    "vector": vector.tolist() if hasattr(vector, 'tolist') else vector
                }
                new_results.append(embedding_data)

                # Cache the embedding
                await self.cache_manager.set(cache_key, vector)

        return cached_results + new_results

class OptimizedVectorDatabase:
    """Simplified vector database"""

    def __init__(self):
        self.vectors = None
        self.chunk_ids = []
        self.chunks = []
        self._index_built = False

    @error_handler
    def build_index(self, embeddings: List[Dict[str, Any]], chunks: List[Dict[str, Any]]) -> None:
        """Build vector index"""
        if not embeddings:
            raise RetrievalError("No embeddings provided for index building")

        vectors = []
        chunk_ids = []

        for emb in embeddings:
            vectors.append(emb["vector"])
            chunk_ids.append(emb["chunk_id"])

        self.vectors = np.array(vectors, dtype=np.float32)
        self.chunk_ids = chunk_ids
        self.chunks = chunks
        self._index_built = True

        logger.info(f"Built vector index with {len(vectors)} embeddings")

    async def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search vector index"""
        if not self._index_built:
            raise RetrievalError("Vector index not built")

        # Compute cosine similarity
        similarities = cosine_similarity(query_vector, self.vectors)

        # Get top-k results
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            # Get similarity score and ensure it's a scalar
            similarity_score = float(similarities[idx])

            if similarity_score > 0.1:  # Minimum similarity threshold
                chunk_id = self.chunk_ids[idx]
                chunk = next((c for c in self.chunks if c["chunk_id"] == chunk_id), None)

                if chunk:
                    results.append({
                        "chunk_id": chunk_id,
                        "text": chunk["text"],
                        "score": similarity_score,
                        "doc_id": chunk["doc_id"]
                    })

        return results

class OptimizedReranker:
    """Simplified reranker with caching"""

    def __init__(self, model_name: str, cache_manager: SimpleCache):
        self.model_name = model_name
        self.cache_manager = cache_manager
        self._model = None

    def _get_model(self):
        """Lazy load reranker model"""
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
                import torch

                # Check for CUDA availability and use it if available
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self._model = CrossEncoder(self.model_name, device=device)
                logger.info(f"Loaded reranker model: {self.model_name} on {device}")
            except Exception as e:
                logger.error(f"Failed to load reranker model: {e}")
                raise EmbeddingError(f"Could not load reranker {self.model_name}: {e}")
        return self._model

    @cache_result(SimpleCache(config.cache_dir), ttl=3600)
    async def rerank(self, query: str, chunks: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """Rerank chunks with caching"""
        if not chunks:
            return []

        # Generate cache key
        chunk_texts = [c["text"][:100] for c in chunks]
        cache_key = f"rerank:{hash(query)}:{hash(tuple(chunk_texts))}"

        # Check cache
        cached = await self.cache_manager.get(cache_key)
        if cached:
            logger.info("Reranker result found in cache")
            return cached

        # Generate pairs for reranking
        pairs = [(query, chunk["text"]) for chunk in chunks]

        try:
            model = self._get_model()
            scores = model.predict(pairs)

            results = []
            for chunk, score in zip(chunks, scores):
                results.append({
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk["text"],
                    "score": float(score),
                    "doc_id": chunk.get("doc_id", "")
                })

            # Sort by score and return top_k
            ranked = sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]

            # Cache result
            await self.cache_manager.set(cache_key, ranked)

            return ranked

        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            # Return original chunks if reranking fails
            return chunks[:top_k]

class OptimizedRAGSystem:
    """
    Simplified Optimized Universal RAG System
    """

    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        # Apply config overrides if provided
        if config_override:
            for key, value in config_override.items():
                if hasattr(config, key):
                    setattr(config, key, value)

        # Create directories
        config.create_directories()

        # Initialize components
        self.cache_manager = SimpleCache(config.cache_dir, config.cache_ttl)

        # Initialize RAG components
        self.embedding_service = OptimizedEmbeddingService(
            config.embedding_model, self.cache_manager
        )
        self.vector_db = OptimizedVectorDatabase()
        self.reranker = OptimizedReranker(config.reranker_model, self.cache_manager)

        # System state
        self.documents = []
        self.chunks = []
        self.bm25_index = {}
        self.best_config = {}
        self._initialized = False

        logger.info("Optimized RAG System initialized")

    @async_error_handler
    async def initialize_system(self) -> bool:
        """Initialize the RAG system with documents"""
        try:
            logger.info("🔧 Initializing Optimized RAG System...")

            # Load documents
            docs = load_documents({"data_dir": config.data_dir}).get("documents", [])
            if not docs:
                logger.warning("⚠️ No documents found! System will run in empty mode.")
                self.documents = []
                self.chunks = []
                self._initialized = True
                logger.info("✅ RAG System initialized (empty mode)")
                return True

            self.documents = docs
            logger.info(f"✅ Loaded {len(docs)} documents")

            # Load best configuration
            try:
                with open("RAG_Logic/results/summary.json", "r", encoding="utf-8") as f:
                    summary = json.load(f)
                self.best_config = summary["best_config"]
                logger.info(f"✅ Loaded best config: {self.best_config}")
            except FileNotFoundError:
                self.best_config = {
                    "chunk_size": config.chunk_size,
                    "overlap": config.overlap,
                    "embedding_model": config.embedding_model,
                    "vector_weight": config.vector_weight,
                    "keyword_weight": config.keyword_weight,
                    "top_k": config.top_k
                }
                logger.info("⚠️ Using default configuration")

            # Chunk documents
            chunks_result = chunk_documents({
                "documents": self.documents,
                "config": {
                    "chunk_size": self.best_config["chunk_size"],
                    "overlap": self.best_config["overlap"]
                }
            })
            self.chunks = chunks_result["chunks"]
            logger.info(f"✅ Created {len(self.chunks)} chunks")

            # Generate embeddings
            embeddings = await self.embedding_service.generate_embeddings(self.chunks)
            logger.info(f"✅ Generated embeddings for {len(embeddings)} chunks")

            # Build vector index
            self.vector_db.build_index(embeddings, self.chunks)
            logger.info(f"✅ Built vector index")

            # Build BM25 index
            self.bm25_index = build_bm25_index({"chunks": self.chunks})
            logger.info(f"✅ Built BM25 index")

            self._initialized = True
            logger.info("🎉 Optimized RAG System initialized successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Error initializing RAG system: {e}")
            return False

    @async_error_handler
    async def retrieve_relevant_info(self, query: str) -> Dict[str, Any]:
        """Retrieve relevant information using hybrid search"""
        if not self._initialized:
            raise RetrievalError("RAG system not initialized")

        try:
            # Generate query embedding
            query_embeddings = await self.embedding_service.generate_embeddings([
                {"chunk_id": "query", "doc_id": "query", "text": query}
            ])

            if not query_embeddings:
                raise RetrievalError("Failed to generate query embedding")

            query_vector = np.array(query_embeddings[0]["vector"])

            # Semantic search
            semantic_results = await self.vector_db.search(
                query_vector, top_k=self.best_config["top_k"] * 2
            )

            # Keyword search
            keyword_results = bm25_search({
                "query": query,
                "bm25": self.bm25_index["bm25"],
                "chunks": self.chunks,
                "top_k": self.best_config["top_k"] * 2
            })["results"]

            # RRF fusion
            fused_results = reciprocal_rank_fusion(semantic_results, keyword_results)

            # Rerank results
            candidate_chunks = fused_results[:10]  # Limit reranker input
            reranked = await self.reranker.rerank(query, candidate_chunks, top_k=self.best_config["top_k"])

            return {
                "results": reranked,
                "semantic_count": len(semantic_results),
                "keyword_count": len(keyword_results),
                "fusion_count": len(fused_results),
                "reranked_count": len(reranked)
            }

        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            raise RetrievalError(f"Retrieval failed: {e}")

    @async_error_handler
    async def generate_answer(self, query: str, retrieval_results: Dict[str, Any]) -> str:
        """Generate answer using Ollama"""
        import aiohttp

        context = "\n\n".join([r.get("text", "") for r in retrieval_results.get("results", [])])

        if not context:
            return "No relevant context found to answer this query."

        prompt = f"""
Answer the question based ONLY on the context.

Context:
{context}

Question: {query}

Answer:
"""

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{config.ollama_base_url}/api/generate",
                    json={
                        "model": config.ollama_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0}
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:

                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "No response generated")
                    else:
                        error_text = await response.text()
                        logger.error(f"Ollama API error {response.status}: {error_text}")
                        raise GenerationError(f"Ollama API returned status {response.status}")

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise GenerationError(f"Error generating answer: {e}")

    @async_error_handler
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Main method to process a query"""
        logger.info(f"🔍 Processing query: {query}")

        # Handle empty mode - no documents loaded
        if not self.documents:
            return {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "rag_analysis": {
                    "retrieved_chunks_count": 0,
                    "top_chunks": [],
                    "retrieval_method": "empty_mode",
                    "semantic_count": 0,
                    "keyword_count": 0,
                    "reranked_count": 0,
                    "message": "No documents loaded - please upload documents first"
                },
                "answer": "I don't have access to any documents yet. Please upload some documents to the system first, and then I can help you find information.",
                "confidence_score": 0.0,
                "source_documents": []
            }

        # Step 1: Retrieve relevant information
        retrieval_results = await self.retrieve_relevant_info(query)

        # Step 2: Generate answer
        answer = await self.generate_answer(query, retrieval_results)

        # Step 3: Combine results
        final_result = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "rag_analysis": {
                "retrieved_chunks_count": len(retrieval_results.get("results", [])),
                "top_chunks": retrieval_results.get("results", [])[:3],
                "retrieval_method": "optimized_hybrid_vector_keyword",
                "semantic_count": retrieval_results.get("semantic_count", 0),
                "keyword_count": retrieval_results.get("keyword_count", 0),
                "reranked_count": retrieval_results.get("reranked_count", 0)
            },
            "answer": answer,
            "confidence_score": self._calculate_confidence(retrieval_results),
            "source_documents": self._get_source_documents(retrieval_results)
        }

        logger.info(f"✅ Query processed successfully")
        return final_result

    def _calculate_confidence(self, retrieval_results: Dict[str, Any]) -> float:
        """Calculate confidence score"""
        results = retrieval_results.get("results", [])
        if not results:
            return 0.0

        # Base confidence from number of results
        base_confidence = min(len(results) / 10.0, 1.0)

        # Factor in average score
        if results and results[0].get("score"):
            avg_score = sum(r.get("score", 0) for r in results[:3]) / min(3, len(results))
            return (base_confidence + avg_score) / 2.0

        return base_confidence

    def _get_source_documents(self, retrieval_results: Dict[str, Any]) -> List[str]:
        """Extract source document names"""
        sources = set()
        for result in retrieval_results.get("results", []):
            source = result.get("doc_id") or result.get("source")
            if source:
                sources.add(str(source))
        return list(sources)

    async def clear_cache(self) -> None:
        """Clear all cache entries"""
        await self.cache_manager.clear()

# Global instance for web service
rag_system: Optional[OptimizedRAGSystem] = None

async def get_rag_system() -> OptimizedRAGSystem:
    """Get or create global RAG system instance"""
    global rag_system

    if rag_system is None:
        rag_system = OptimizedRAGSystem()
        await rag_system.initialize_system()

    return rag_system
