"""
Simple utility functions for error handling and caching
"""

import asyncio
import functools
import hashlib
import json
import logging
import pickle
import time
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path
import aiofiles
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class RAGError(Exception):
    """Base exception for RAG system"""
    pass

class ConfigurationError(RAGError):
    """Configuration related errors"""
    pass

class DocumentLoadError(RAGError):
    """Document loading errors"""
    pass

class EmbeddingError(RAGError):
    """Embedding generation errors"""
    pass

class RetrievalError(RAGError):
    """Retrieval system errors"""
    pass

class GenerationError(RAGError):
    """Answer generation errors"""
    pass

def error_handler(func: Callable) -> Callable:
    """Decorator for comprehensive error handling"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)

            # Map specific exceptions to custom ones
            if "configuration" in str(e).lower():
                raise ConfigurationError(f"Configuration error in {func.__name__}: {e}")
            elif "document" in str(e).lower():
                raise DocumentLoadError(f"Document loading error in {func.__name__}: {e}")
            elif "embedding" in str(e).lower():
                raise EmbeddingError(f"Embedding error in {func.__name__}: {e}")
            elif "retrieval" in str(e).lower():
                raise RetrievalError(f"Retrieval error in {func.__name__}: {e}")
            elif "generation" in str(e).lower():
                raise GenerationError(f"Generation error in {func.__name__}: {e}")
            else:
                raise RAGError(f"Unexpected error in {func.__name__}: {e}")

    return wrapper

def async_error_handler(func: Callable) -> Callable:
    """Decorator for async error handling"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)

            # Map specific exceptions to custom ones
            if "configuration" in str(e).lower():
                raise ConfigurationError(f"Configuration error in {func.__name__}: {e}")
            elif "document" in str(e).lower():
                raise DocumentLoadError(f"Document loading error in {func.__name__}: {e}")
            elif "embedding" in str(e).lower():
                raise EmbeddingError(f"Embedding error in {func.__name__}: {e}")
            elif "retrieval" in str(e).lower():
                raise RetrievalError(f"Retrieval error in {func.__name__}: {e}")
            elif "generation" in str(e).lower():
                raise GenerationError(f"Generation error in {func.__name__}: {e}")
            else:
                raise RAGError(f"Unexpected error in {func.__name__}: {e}")

    return wrapper

class SimpleCache:
    """Simple file-based cache with TTL support"""

    def __init__(self, cache_dir: str, default_ttl: int = 3600):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl

    def _get_cache_key(self, key: str) -> str:
        """Generate cache key from input"""
        return hashlib.md5(key.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get file path for cache key"""
        return self.cache_dir / f"{cache_key}.cache"

    def _is_expired(self, cache_data: Dict[str, Any]) -> bool:
        """Check if cache entry is expired"""
        if 'timestamp' not in cache_data:
            return True

        age = time.time() - cache_data['timestamp']
        return age > cache_data.get('ttl', self.default_ttl)

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        cache_key = self._get_cache_key(key)
        cache_path = self._get_cache_path(cache_key)

        if cache_path.exists():
            try:
                async with aiofiles.open(cache_path, 'rb') as f:
                    cache_data = pickle.loads(await f.read())

                if not self._is_expired(cache_data):
                    return cache_data['data']
                else:
                    # Remove expired file
                    cache_path.unlink()
            except Exception as e:
                logger.warning(f"Cache read error for {key}: {e}")
                cache_path.unlink(missing_ok=True)

        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        cache_key = self._get_cache_key(key)
        ttl = ttl or self.default_ttl

        cache_data = {
            'data': value,
            'timestamp': time.time(),
            'ttl': ttl
        }

        cache_path = self._get_cache_path(cache_key)
        try:
            async with aiofiles.open(cache_path, 'wb') as f:
                await f.write(pickle.dumps(cache_data))
        except Exception as e:
            logger.warning(f"Cache write error for {key}: {e}")

    async def clear(self) -> None:
        """Clear all cache entries"""
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                cache_file.unlink()
            except Exception as e:
                logger.warning(f"Cache cleanup error: {e}")

def cache_result(cache_manager: SimpleCache, ttl: Optional[int] = None):
    """Decorator for caching function results"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"

            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            await cache_manager.set(cache_key, result, ttl)
            return result

        return wrapper
    return decorator

class BatchProcessor:
    """Process items in batches for better performance"""

    def __init__(self, batch_size: int = 32, max_workers: int = 4):
        self.batch_size = batch_size
        self.max_workers = max_workers

    def process_batches(self, items: List[Any], process_func: Callable) -> List[Any]:
        """Process items in batches using ThreadPoolExecutor"""
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Create batches
            batches = [
                items[i:i + self.batch_size]
                for i in range(0, len(items), self.batch_size)
            ]

            # Process batches in parallel
            futures = [
                executor.submit(process_func, batch)
                for batch in batches
            ]

            # Collect results
            for future in futures:
                try:
                    batch_results = future.result()
                    results.extend(batch_results)
                except Exception as e:
                    logger.error(f"Batch processing error: {e}")
                    results.extend([None] * self.batch_size)  # Placeholder for failed batch

        return results

@dataclass
class PerformanceMetrics:
    """Simple performance metrics tracking"""
    query_count: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    error_count: int = 0

    def update(self, duration: float, cache_hit: bool = False, error: bool = False) -> None:
        """Update metrics with new query data"""
        self.query_count += 1
        self.total_time += duration
        self.avg_time = self.total_time / self.query_count

        if cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

        if error:
            self.error_count += 1

    def get_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.cache_hits + self.cache_misses
        return (self.cache_hits / total * 100) if total > 0 else 0.0

    def get_error_rate(self) -> float:
        """Calculate error rate"""
        return (self.error_count / self.query_count * 100) if self.query_count > 0 else 0.0

# Global instances
performance_metrics = PerformanceMetrics()
