"""
Simple Configuration Management for Universal RAG System
"""

import os
from typing import Dict, Any
from dataclasses import dataclass

def check_cuda_available():
    """Check if CUDA is available for PyTorch"""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False

def get_device_info():
    """Get device information for PyTorch"""
    try:
        import torch
        if torch.cuda.is_available():
            return {
                "device": "cuda",
                "device_count": torch.cuda.device_count(),
                "device_name": torch.cuda.get_device_name(0),
                "device_memory": torch.cuda.get_device_properties(0).total_memory
            }
        else:
            return {"device": "cpu"}
    except ImportError:
        return {"device": "cpu"}

@dataclass
class RAGConfig:
    """Simple configuration class for RAG system settings"""

    # Model Settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L12-v2"
    reranker_model: str = "BAAI/bge-reranker-base"
    ollama_model: str = "llama3"
    ollama_base_url: str = "http://localhost:11434"

    # Chunking Settings
    chunk_size: int = 400
    overlap: int = 50

    # Retrieval Settings
    top_k: int = 5
    vector_weight: float = 0.5
    keyword_weight: float = 0.5

    # Performance Settings
    embedding_batch_size: int = 32
    cache_ttl: int = 3600  # 1 hour

    # File Paths
    data_dir: str = "RAG_Logic/data/documents"
    cache_dir: str = "RAG_Logic/cache"
    logs_dir: str = "RAG_Logic/logs"

    # Web Service Settings
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # Device Settings
    force_cpu: bool = False  # Force CPU even if CUDA is available

    @classmethod
    def from_env(cls) -> 'RAGConfig':
        """Create configuration from environment variables"""
        config = cls()

        # Override with environment variables
        env_mappings = {
            'RAG_EMBEDDING_MODEL': 'embedding_model',
            'RAG_RERANKER_MODEL': 'reranker_model',
            'RAG_OLLAMA_MODEL': 'ollama_model',
            'RAG_OLLAMA_URL': 'ollama_base_url',
            'RAG_CHUNK_SIZE': 'chunk_size',
            'RAG_OVERLAP': 'overlap',
            'RAG_TOP_K': 'top_k',
            'RAG_DATA_DIR': 'data_dir',
            'RAG_HOST': 'host',
            'RAG_PORT': 'port',
            'RAG_LOG_LEVEL': 'log_level',
            'RAG_FORCE_CPU': 'force_cpu',
        }

        for env_var, config_attr in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Handle numeric values
                if config_attr in ['chunk_size', 'overlap', 'top_k', 'port']:
                    setattr(config, config_attr, int(env_value))
                elif config_attr in ['vector_weight', 'keyword_weight']:
                    setattr(config, config_attr, float(env_value))
                elif config_attr == 'force_cpu':
                    setattr(config, config_attr, env_value.lower() in ('true', '1', 'yes'))
                else:
                    setattr(config, config_attr, env_value)

        return config

    def get_device(self) -> str:
        """Get the device to use for PyTorch models"""
        if self.force_cpu:
            return "cpu"

        if check_cuda_available():
            return "cuda"
        else:
            return "cpu"

    def create_directories(self) -> None:
        """Create necessary directories"""
        import os
        from pathlib import Path

        directories = [
            self.data_dir,
            self.cache_dir,
            self.logs_dir,
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

# Global configuration instance
config = RAGConfig.from_env()

def setup_logging() -> None:
    """Setup logging configuration"""
    import logging

    config.create_directories()

    log_file = os.path.join(config.logs_dir, "rag_system.log")

    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    # Log device information
    device_info = get_device_info()
    logging.info(f"🔥 Device Info: {device_info}")
    if device_info.get("device") == "cuda":
        logging.info(f"🚀 Using GPU: {device_info.get('device_name', 'Unknown')}")
        logging.info(f"💾 GPU Memory: {device_info.get('device_memory', 0) / 1024**3:.1f} GB")
    else:
        logging.info("💻 Using CPU for PyTorch operations")
