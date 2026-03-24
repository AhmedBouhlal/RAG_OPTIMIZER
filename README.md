# Universal RAG System

A high-performance, domain-agnostic Retrieval-Augmented Generation (RAG) system that combines document retrieval with AI generation for intelligent question answering across any topic.

## 🚀 Features

### Core Capabilities
- **Universal Document Support**: Handles PDF, DOCX, TXT, HTML, CSV, and JSON files
- **Hybrid Retrieval**: Combines vector search with keyword matching (BM25)
- **Intelligent Reranking**: Uses advanced reranking for better relevance
- **Flexible Configuration**: Optimized chunking and embedding parameters
- **Domain Agnostic**: Works with any type of documents and questions

### Performance Features
- **Async Architecture**: High-performance async/await support
- **Intelligent Caching**: Multi-layer caching with TTL support
- **Batch Processing**: Efficient batch processing for embeddings
- **Error Handling**: Comprehensive error handling and recovery
- **Web Service**: FastAPI-based REST API

## 📁 Project Structure

```
AUTO_RAG/
├── config.py                    # Configuration management
├── utils.py                      # Utility functions and caching
├── optimized_logic.py            # Optimized RAG system
├── web_service.py                # FastAPI web service
├── performance_test.py           # Performance testing
├── logic.py                      # Original CLI version
├── requirements.txt              # Dependencies
└── RAG_Logic/                   # Core RAG components
    ├── src/                     # RAG modules
    ├── data/documents/          # Document storage
    ├── cache/                   # Cache storage
    └── logs/                    # Log storage
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- Ollama (for local LLM inference)

### 2. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3
```

### 3. Add Documents

```bash
# Create documents directory
mkdir -p RAG_Logic/data/documents

# Add your documents
cp your-documents/* RAG_Logic/data/documents/
```

### 4. Run the System

#### Option A: Web Service (Recommended)

```bash
# Start the web service
python web_service.py

# The API will be available at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

#### Option B: CLI Interface

```bash
# Run the original CLI
python logic.py
```

### 5. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Query the system
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the main causes of climate change?"}'
```

## 📖 API Documentation

### Query Endpoint

```http
POST /query
Content-Type: application/json

{
  "query": "Your question here",
  "top_k": 5,
  "include_sources": true
}
```

**Response:**
```json
{
  "query": "Your question here",
  "answer": "Generated answer based on retrieved context...",
  "confidence_score": 0.85,
  "source_documents": ["doc1.pdf", "doc2.txt"],
  "timestamp": "2024-01-01T12:00:00Z",
  "rag_analysis": {
    "retrieved_chunks_count": 5,
    "top_chunks": [...],
    "retrieval_method": "optimized_hybrid_vector_keyword"
  }
}
```

### Health Check

```http
GET /health
```

### Configuration

```http
GET /config
```

## ⚙️ Configuration

### Environment Variables

```bash
# Service Configuration
RAG_HOST=0.0.0.0
RAG_PORT=8000
RAG_LOG_LEVEL=INFO

# Model Configuration
RAG_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L12-v2
RAG_RERANKER_MODEL=BAAI/bge-reranker-base
RAG_OLLAMA_MODEL=llama3
RAG_OLLAMA_URL=http://localhost:11434

# Performance Configuration
RAG_CHUNK_SIZE=400
RAG_OVERLAP=50
RAG_TOP_K=5
RAG_CACHE_TTL=3600

# Paths
RAG_DATA_DIR=RAG_Logic/data/documents
RAG_CACHE_DIR=RAG_Logic/cache
```

## 🧪 Experimentation & Optimization

The system includes a complete experimentation framework to test different configurations and find optimal settings.

### Quick Experiment

```bash
# Run a quick experiment to generate optimal configuration
python quick_experiment.py

# This will:
# 1. Test different RAG configurations
# 2. Evaluate against sample queries
# 3. Generate summary.json with best config
# 4. Automatically optimize the main system
```

### Complete Experiment Suite

```bash
# Run full experiment suite with multiple configurations
python run_experiments.py

# View detailed results
cat RAG_Logic/results/summary.json
```

### Custom Evaluation Data

Add your own evaluation queries in JSON format:

```bash
# Create evaluation file
mkdir -p RAG_Logic/data/evaluation
```

**Evaluation JSON Format:**
```json
[
  {
    "query": "What are the main causes of climate change?",
    "answer": ["greenhouse gases", "fossil fuels", "deforestation"]
  },
  {
    "query": "How does photosynthesis work?",
    "answer": ["chlorophyll", "sunlight", "CO2", "oxygen"]
  }
]
```

### Experiment Configurations

The system tests different configurations:

- **Chunk Size**: 150-600 words
- **Overlap**: 0-100 words
- **Top K**: 3-10 results
- **Vector/Keyword Weights**: 0.3-0.7
- **Reranking**: 8-15 candidates

### Results

After running experiments, the system generates:

- `RAG_Logic/results/summary.json` - Best configuration
- Individual experiment results
- Performance metrics and rankings
- Retrieval examples

The main RAG system automatically uses the best configuration from experiments.

## 🔧 Performance Optimization

### Caching System

The system includes intelligent caching:
- **Embedding Cache**: Caches generated embeddings to avoid recomputation
- **Reranker Cache**: Caches reranking results for common queries
- **TTL Support**: Configurable time-to-live for cache entries
- **Automatic Cleanup**: Background cleanup of expired entries

### Batch Processing

- **Embedding Batches**: Processes embeddings in batches for efficiency
- **Parallel Processing**: Uses ThreadPoolExecutor for CPU-bound tasks
- **Memory Optimization**: Efficient memory usage for large datasets

### Performance Monitoring

```bash
# Run performance tests
python performance_test.py

# Check service health
curl http://localhost:8000/health

# Monitor logs
tail -f RAG_Logic/logs/rag_system.log
```

## 📊 Usage Examples

### CLI Examples

```python
# Using the CLI
python logic.py

# Example questions:
- "What are the main causes of climate change?"
- "Explain the principles of machine learning."
- "How does photosynthesis work in plants?"
- "What are the benefits of meditation?"
```

### Web Service Examples

```python
import requests

# Query the RAG system
response = requests.post("http://localhost:8000/query", json={
    "query": "What are the main causes of climate change?",
    "top_k": 5,
    "include_sources": True
})

result = response.json()
print(result["answer"])
print(f"Confidence: {result['confidence_score']}")
print(f"Sources: {result['source_documents']}")
```

## 🧪 Performance Testing

```bash
# Run performance tests
python performance_test.py

# Example output:
✅ Load test completed:
   Total queries: 50
   Success rate: 98.0%
   Queries/sec: 25.3
   Avg response time: 1.234s
   P95 response time: 2.156s
   Avg confidence: 0.82
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Service Won't Start

```bash
# Check logs
tail -f RAG_Logic/logs/rag_system.log

# Check configuration
python -c "from config import config; print(config.validate())"
```

#### 2. Ollama Connection Issues

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Restart Ollama
systemctl restart ollama
```

#### 3. Slow Response Times

```bash
# Clear cache
curl -X POST http://localhost:8000/cache/clear

# Check performance metrics
curl http://localhost:8000/metrics
```

### Performance Tips

- **Use smaller models** for faster inference
- **Increase batch size** for better GPU utilization
- **Cache embeddings** for frequently used documents
- **Adjust top_k values** for balance between speed and quality

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Service   │    │   Cache Layer   │    │  External APIs  │
│   (FastAPI)     │◄──►│   (File-based)  │◄──►│   (Ollama)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Optimized RAG System                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │ Embeddings  │ │ Vector DB   │ │ BM25 Index  │ │ Reranker    │ │
│  │ Service     │ │            │ │             │ │             │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 📝 Development

### Running Tests

```bash
# Run performance tests
python performance_test.py

# Test API endpoints
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Test query"}'
```

### Adding New Features

1. **New Document Types**: Extend `RAG_Logic/src/loader.py`
2. **Custom Embeddings**: Modify `optimized_logic.py`
3. **New Retrieval Methods**: Add to RAG components

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- **Issues**: Create an issue on GitHub for bugs and feature requests
- **Documentation**: Check the inline documentation and comments
- **Performance**: Use the performance testing suite to diagnose issues

## 🔄 Migration from Original

If you're upgrading from the original system:

1. **Install new dependencies**: `pip install -r requirements.txt`
2. **Start web service**: `python web_service.py` instead of `python logic.py`
3. **Use HTTP API**: Make HTTP requests instead of direct function calls
4. **Monitor performance**: Use `/health` endpoint for monitoring

The optimized version maintains full compatibility with the original RAG components while adding significant performance improvements and web service capabilities.
