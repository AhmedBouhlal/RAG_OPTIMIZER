"""
Optimized CLI Interface for RAG System
Interactive command-line interface with optimized configuration
"""

import sys
import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

# Add RAG_Logic to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'RAG_Logic'))

# Import optimized components
from config import config, setup_logging
from logic import get_rag_system, OptimizedRAGSystem
from utils import performance_metrics, RAGError, RetrievalError, GenerationError

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class OptimizedRAGCLI:
    """Interactive CLI for the optimized RAG system"""

    def __init__(self):
        self.rag_system: Optional[OptimizedRAGSystem] = None
        self.conversation_history = []
        self.start_time = time.time()

    async def initialize(self) -> bool:
        """Initialize the RAG system"""
        try:
            print("🚀 Initializing Optimized RAG System...")
            print("="*50)

            # Load best configuration if available
            best_config = self._load_best_config()
            if best_config:
                print("✅ Using optimized configuration from experiments")
                print(f"   📊 Best Score: {best_config.get('best_score', 'N/A')}")
                config_data = best_config.get('best_config', {})
                print(f"   🎯 Chunk Size: {config_data.get('chunk_size', 'N/A')}")
                print(f"   🔍 Top-K: {config_data.get('top_k', 'N/A')}")
                print(f"   ⚖️ Vector Weight: {config_data.get('vector_weight', 'N/A')}")
            else:
                print("⚠️ No optimized configuration found, using defaults")

            # Initialize RAG system
            self.rag_system = await get_rag_system()

            if self.rag_system and self.rag_system._initialized:
                print("✅ RAG System initialized successfully!")
                print(f"📚 Documents loaded: {len(self.rag_system.documents)}")
                print(f"🔤 Chunks created: {len(self.rag_system.chunks)}")
                print(f"🧪 Evaluation queries: {len(self.rag_system.ground_truths) if hasattr(self.rag_system, 'ground_truths') else 'N/A'}")
                return True
            else:
                print("❌ Failed to initialize RAG system")
                return False

        except Exception as e:
            print(f"❌ Error initializing RAG system: {e}")
            return False

    def _load_best_config(self) -> Optional[Dict[str, Any]]:
        """Load best configuration from experiments"""
        try:
            summary_file = "RAG_Logic/results/summary.json"
            if os.path.exists(summary_file):
                with open(summary_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load best config: {e}")
        return None

    def print_welcome(self) -> None:
        """Print welcome message and help"""
        print("\n" + "="*60)
        print("🤖 OPTIMIZED RAG SYSTEM - Interactive CLI")
        print("="*60)
        print("\n💡 Available commands:")
        print("   • Type your question directly (e.g., 'What is RAG?')")
        print("   • '/help' - Show this help message")
        print("   • '/stats' - Show performance statistics")
        print("   • '/config' - Show current configuration")
        print("   • '/history' - Show conversation history")
        print("   • '/clear' - Clear conversation history")
        print("   • '/benchmark' - Run quick benchmark")
        print("   • '/quit' or 'exit' - Exit the program")
        print("\n🎯 Example questions:")
        print("   • 'What are the main components of a RAG system?'")
        print("   • 'How does document chunking work?'")
        print("   • 'What is vector search in RAG?'")
        print("   • 'How can I optimize RAG performance?'")
        print("\n" + "="*60)

    def print_help(self) -> None:
        """Print detailed help information"""
        print("\n📚 DETAILED HELP")
        print("="*40)
        print("\n🔍 QUERY TYPES:")
        print("   • Factual questions: 'What is...?'")
        print("   • Explanatory: 'How does... work?'")
        print("   • Comparative: 'What is the difference between...?'")
        print("   • Procedural: 'How to...?'")
        print("\n⚙️ SYSTEM FEATURES:")
        print("   • Hybrid retrieval (vector + keyword search)")
        print("   • Intelligent reranking for better results")
        print("   • CUDA GPU acceleration (if available)")
        print("   • Performance caching for faster responses")
        print("   • Comprehensive error handling")
        print("\n📊 PERFORMANCE METRICS:")
        print("   • Response time tracking")
        print("   • Cache hit rate monitoring")
        print("   • Success rate measurement")
        print("   • Confidence scoring")
        print("\n💡 TIPS:")
        print("   • Be specific in your questions")
        print("   • Use complete sentences")
        print("   • Ask follow-up questions for clarification")
        print("   • Check '/stats' for performance info")
        print("="*40)

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process a user query"""
        if not self.rag_system:
            return {"error": "RAG system not initialized"}

        start_time = time.time()

        try:
            # Process query
            result = await self.rag_system.process_query(query)

            # Calculate response time
            response_time = time.time() - start_time

            # Update performance metrics
            performance_metrics.update(response_time)

            # Add to conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "response": result.get("answer", ""),
                "confidence": result.get("confidence_score", 0),
                "response_time": response_time,
                "sources": result.get("source_documents", [])
            })

            return result

        except RetrievalError as e:
            return {"error": f"Retrieval failed: {e}"}
        except GenerationError as e:
            return {"error": f"Generation failed: {e}"}
        except RAGError as e:
            return {"error": f"RAG system error: {e}"}
        except Exception as e:
            return {"error": f"Unexpected error: {e}"}

    def format_response(self, result: Dict[str, Any]) -> str:
        """Format the response for display"""
        if "error" in result:
            return f"\n❌ Error: {result['error']}"

        response = []
        response.append(f"\n🤖 Answer:")
        response.append(f"   {result['answer']}")

        # Add confidence score
        confidence = result.get("confidence_score", 0)
        confidence_emoji = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.5 else "🔴"
        response.append(f"\n{confidence_emoji} Confidence: {confidence:.2f}")

        # Add sources
        sources = result.get("source_documents", [])
        if sources:
            response.append(f"\n📚 Sources: {', '.join(sources[:3])}")

        # Add RAG analysis
        rag_analysis = result.get("rag_analysis", {})
        if rag_analysis:
            response.append(f"\n🔍 Retrieved {rag_analysis.get('retrieved_chunks_count', 0)} chunks")
            response.append(f"   Method: {rag_analysis.get('retrieval_method', 'unknown')}")

        return "\n".join(response)

    def show_stats(self) -> None:
        """Show performance statistics"""
        print("\n📊 PERFORMANCE STATISTICS")
        print("="*40)

        # System stats
        uptime = time.time() - self.start_time
        print(f"⏱️  Uptime: {uptime:.1f} seconds")
        print(f"💬 Queries processed: {performance_metrics.query_count}")
        print(f"⚡ Avg response time: {performance_metrics.avg_time:.2f}s")
        print(f"🎯 Cache hit rate: {performance_metrics.get_cache_hit_rate():.1f}%")
        print(f"✅ Success rate: {100 - performance_metrics.get_error_rate():.1f}%")

        # Conversation stats
        if self.conversation_history:
            print(f"📝 Conversation history: {len(self.conversation_history)} queries")

            # Average confidence
            avg_confidence = sum(h.get("confidence", 0) for h in self.conversation_history) / len(self.conversation_history)
            print(f"🎯 Average confidence: {avg_confidence:.2f}")

        # System info
        if self.rag_system:
            print(f"📚 Documents: {len(self.rag_system.documents)}")
            print(f"🔤 Chunks: {len(self.rag_system.chunks)}")

        print("="*40)

    def show_config(self) -> None:
        """Show current configuration"""
        print("\n⚙️ CURRENT CONFIGURATION")
        print("="*40)

        # Load best config if available
        best_config = self._load_best_config()
        if best_config:
            config_data = best_config.get('best_config', {})
            print(f"🏆 Best Score: {best_config.get('best_score', 'N/A')}")
            print(f"📊 Chunk Size: {config_data.get('chunk_size', 'N/A')}")
            print(f"📏 Overlap: {config_data.get('overlap', 'N/A')}")
            print(f"🎯 Top-K: {config_data.get('top_k', 'N/A')}")
            print(f"⚖️  Vector Weight: {config_data.get('vector_weight', 'N/A')}")
            print(f"🔤 Keyword Weight: {config_data.get('keyword_weight', 'N/A')}")
            print(f"🤖 Embedding Model: {config_data.get('embedding_model', 'N/A')}")
            print(f"🎯 Rerank Top-K: {config_data.get('rerank_top_k', 'N/A')}")
        else:
            print("⚠️ No optimized configuration found")
            print(f"📊 Default Chunk Size: {config.chunk_size}")
            print(f"🎯 Default Top-K: {config.top_k}")
            print(f"🤖 Default Embedding: {config.embedding_model}")

        # System config
        print(f"\n🔧 System Settings:")
        print(f"   Host: {config.host}")
        print(f"   Port: {config.port}")
        print(f"   Log Level: {config.log_level}")
        print(f"   Cache TTL: {config.cache_ttl}s")
        print(f"   Device: {config.get_device()}")

        print("="*40)

    def show_history(self) -> None:
        """Show conversation history"""
        print("\n📝 CONVERSATION HISTORY")
        print("="*50)

        if not self.conversation_history:
            print("No conversation history yet.")
            return

        for i, entry in enumerate(self.conversation_history[-10:], 1):  # Show last 10
            timestamp = entry.get("timestamp", "")[:19]  # Just time part
            print(f"\n{i}. [{timestamp}]")
            print(f"   Q: {entry.get('query', '')}")
            print(f"   A: {entry.get('response', '')[:100]}...")
            print(f"   🎯 Confidence: {entry.get('confidence', 0):.2f}")
            print(f"   ⏱️  Time: {entry.get('response_time', 0):.2f}s")

        if len(self.conversation_history) > 10:
            print(f"\n... and {len(self.conversation_history) - 10} more queries")

        print("="*50)

    async def run_benchmark(self) -> None:
        """Run a quick benchmark"""
        print("\n🏃 RUNNING BENCHMARK")
        print("="*30)

        benchmark_queries = [
            "What are the main components of a RAG system?",
            "How does document chunking work?",
            "What is vector search?",
            "How does reranking improve results?",
            "What are the benefits of caching?"
        ]

        total_time = 0
        successful = 0

        for i, query in enumerate(benchmark_queries, 1):
            print(f"\n[{i}/{len(benchmark_queries)}] {query}")

            start_time = time.time()
            result = await self.process_query(query)
            response_time = time.time() - start_time

            if "error" not in result:
                successful += 1
                print(f"   ✅ {response_time:.2f}s (Confidence: {result.get('confidence_score', 0):.2f})")
            else:
                print(f"   ❌ {result['error']}")

            total_time += response_time

        # Summary
        avg_time = total_time / len(benchmark_queries)
        success_rate = (successful / len(benchmark_queries)) * 100

        print(f"\n📊 BENCHMARK RESULTS:")
        print(f"   Total queries: {len(benchmark_queries)}")
        print(f"   Successful: {successful}/{len(benchmark_queries)} ({success_rate:.1f}%)")
        print(f"   Average time: {avg_time:.2f}s")
        print(f"   Total time: {total_time:.2f}s")
        print("="*30)

    async def run(self) -> None:
        """Run the interactive CLI"""
        # Initialize system
        if not await self.initialize():
            print("❌ Failed to start RAG system. Exiting.")
            return

        # Show welcome
        self.print_welcome()

        # Main loop
        while True:
            try:
                # Get user input
                query = input("\n💬 Ask a question (or '/help' for commands): ").strip()

                if not query:
                    continue

                # Handle commands
                if query.lower() in ['/quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break

                elif query.lower() == '/help':
                    self.print_help()
                    continue

                elif query.lower() == '/stats':
                    self.show_stats()
                    continue

                elif query.lower() == '/config':
                    self.show_config()
                    continue

                elif query.lower() == '/history':
                    self.show_history()
                    continue

                elif query.lower() == '/clear':
                    self.conversation_history.clear()
                    print("\n🧹 Conversation history cleared.")
                    continue

                elif query.lower() == '/benchmark':
                    await self.run_benchmark()
                    continue

                elif query.startswith('/'):
                    print(f"\n❓ Unknown command: {query}")
                    print("💡 Type '/help' for available commands.")
                    continue

                # Process regular query
                print(f"\n🔍 Processing: {query}")
                print("⏳ Thinking...")

                result = await self.process_query(query)
                response = self.format_response(result)

                print(response)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                continue

def main():
    """Main function"""
    print("🚀 Starting Optimized RAG CLI...")

    # Run the CLI
    cli = OptimizedRAGCLI()
    asyncio.run(cli.run())

if __name__ == "__main__":
    main()
