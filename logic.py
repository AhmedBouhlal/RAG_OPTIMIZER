"""
Integrated RAG + Agentic AI Logic for Forex Trading
Combines RAG system with LangChain tools for intelligent trading decisions
"""

import sys
import os
import json
import requests
from typing import Dict, List, Any, Optional

# Add RAG_Logic to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'RAG_Logic'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'Agentic_AI_Logic'))

# RAG imports
from RAG_Logic.src.loader import load_documents
from RAG_Logic.src.chunking import chunk_documents
from RAG_Logic.src.embedding import generate_embeddings
from RAG_Logic.src.vectordb import build_index
from RAG_Logic.src.keyword_index import build_bm25_index
from RAG_Logic.src.hybrid_retrieval import hybrid_retrieve
from RAG_Logic.src.reranker import Reranker

# Agentic AI imports
from Agentic_AI_Logic.AI_Agent_Logic import TradingDecisionProcessor, get_trading_decision

class IntegratedTradingSystem:
    """
    Integrated system that combines RAG with Agentic AI for forex trading decisions
    """
    
    def __init__(self, 
                 ollama_base_url: str = "http://localhost:11434",
                 ollama_model: str = "llama3",
                 data_dir: str = "RAG_Logic/data/documents"):
        
        self.ollama_base_url = ollama_base_url
        self.ollama_model = ollama_model
        self.data_dir = data_dir
        
        # Initialize RAG components
        self.rag_initialized = False
        self.documents = []
        self.chunks = []
        self.index_dict = {}
        self.bm25_index = {}
        self.reranker = None
        self.best_config = {}
        
        # Initialize Agentic AI
        self.trading_processor = TradingDecisionProcessor()
        
    def initialize_rag_system(self) -> bool:
        """Initialize the RAG system with documents"""
        try:
            print("🔧 Initializing RAG System...")
            
            # Load documents
            docs = load_documents({"data_dir": self.data_dir}).get("documents", [])
            if not docs:
                print("❌ No documents found!")
                return False
            
            self.documents = docs
            print(f"✅ Loaded {len(docs)} documents")
            
            # Load best configuration or use defaults
            try:
                with open("RAG_Logic/results/summary.json", "r", encoding="utf-8") as f:
                    summary = json.load(f)
                self.best_config = summary["best_config"]
                print(f"✅ Loaded best config: {self.best_config}")
            except FileNotFoundError:
                self.best_config = {
                    "chunk_size": 400,
                    "overlap": 50,
                    "embedding_model": "sentence-transformers/all-MiniLM-L12-v2",
                    "vector_weight": 0.5,
                    "keyword_weight": 0.5,
                    "top_k": 5
                }
                print("⚠️ Using default configuration")
            
            # Chunk documents
            chunks = chunk_documents({
                "documents": self.documents,
                "config": {
                    "chunk_size": self.best_config["chunk_size"],
                    "overlap": self.best_config["overlap"]
                }
            })
            self.chunks = chunks["chunks"]
            print(f"✅ Created {len(self.chunks)} chunks")
            
            # Generate embeddings
            embeddings = generate_embeddings({
                "chunks": self.chunks,
                "config": {"embedding_model": self.best_config["embedding_model"]}
            })
            print(f"✅ Generated embeddings")
            
            # Build vector index
            self.index_dict = build_index({
                "chunks": self.chunks,
                "embeddings": embeddings["embeddings"]
            })
            print(f"✅ Built vector index")
            
            # Build BM25 index
            self.bm25_index = build_bm25_index({
                "chunks": self.chunks
            })
            print(f"✅ Built BM25 index")
            
            # Initialize reranker
            self.reranker = Reranker()
            print(f"✅ Initialized reranker")
            
            self.rag_initialized = True
            print("🎉 RAG System initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing RAG system: {e}")
            return False
    
    def rag_generate(self, query: str, retrieval_results: Dict[str, Any]) -> str:
        """Generate answer using Ollama"""
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
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0}
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response generated")
            else:
                return f"Error: Ollama API returned status {response.status_code}"
                
        except Exception as e:
            return f"Error generating answer: {e}"
    
    def retrieve_relevant_info(self, query: str) -> Dict[str, Any]:
        """Retrieve relevant information using RAG system"""
        if not self.rag_initialized:
            return {"error": "RAG system not initialized"}
        
        try:
            # Hybrid retrieval
            retrieval = hybrid_retrieve({
                "query": query,
                "config": self.best_config,
                "index": self.index_dict["index"],
                "chunks": self.index_dict["chunks"],
                "bm25": self.bm25_index["bm25"]
            })
            
            # Rerank results
            candidate_chunks = retrieval.get("results", [])[:20]
            reranked = self.reranker.rerank(query, candidate_chunks, top_k=self.best_config["top_k"])
            retrieval["results"] = reranked
            
            return retrieval
            
        except Exception as e:
            return {"error": f"Retrieval failed: {e}"}
    
    def get_trading_decision(self, query: str) -> Dict[str, Any]:
        """
        Main method to get trading decision for a query
        
        Args:
            query: User's trading question
            
        Returns:
            Structured trading decision with RAG analysis and agent recommendations
        """
        print(f"\n🔍 Processing query: {query}")
        
        # Step 1: Retrieve relevant information using RAG
        retrieval_results = self.retrieve_relevant_info(query)
        
        if "error" in retrieval_results:
            return {
                "query": query,
                "error": retrieval_results["error"],
                "trading_decisions": []
            }
        
        print(f"📊 Retrieved {len(retrieval_results.get('results', []))} relevant chunks")
        
        # Step 2: Generate RAG answer
        rag_answer = self.rag_generate(query, retrieval_results)
        print(f"💬 Generated RAG answer")
        
        # Step 3: Process with Agentic AI for structured trading decisions
        trading_analysis = self.trading_processor.process_rag_query(query, rag_answer)
        print(f"🤖 Processed with Agentic AI")
        
        # Step 4: Combine all results
        final_result = {
            "query": query,
            "timestamp": trading_analysis["timestamp"],
            "rag_analysis": {
                "retrieved_chunks_count": len(retrieval_results.get("results", [])),
                "top_chunks": retrieval_results.get("results", [])[:3],
                "rag_answer": rag_answer
            },
            "trading_decisions": trading_analysis["trading_decisions"],
            "currency_pairs": trading_analysis["currency_pairs"],
            "overall_sentiment": trading_analysis["overall_sentiment"],
            "confidence_score": trading_analysis["confidence_score"],
            "analysis_method": trading_analysis["analysis_method"],
            "agent_analysis": trading_analysis["raw_analysis"]
        }
        
        return final_result
    
    def format_trading_output(self, result: Dict[str, Any]) -> str:
        """Format the trading result for display"""
        if "error" in result:
            return f"❌ Error: {result['error']}"
        
        output = []
        output.append("=" * 60)
        output.append(f"📈 TRADING ANALYSIS FOR: {result['query'].upper()}")
        output.append("=" * 60)
        output.append(f"⏰ Timestamp: {result['timestamp']}")
        output.append(f"📊 Overall Sentiment: {result['overall_sentiment'].upper()}")
        output.append(f"🎯 Confidence Score: {result['confidence_score']:.2f}")
        output.append("")
        
        # RAG Analysis Summary
        output.append("📚 RAG ANALYSIS SUMMARY:")
        rag_analysis = result["rag_analysis"]
        output.append(f"   • Retrieved {rag_analysis['retrieved_chunks_count']} relevant chunks")
        output.append(f"   • RAG Answer: {rag_analysis['rag_answer'][:200]}...")
        output.append("")
        
        # Trading Decisions
        decisions = result["trading_decisions"]
        if decisions:
            output.append("💰 TRADING DECISIONS:")
            for i, decision in enumerate(decisions, 1):
                if isinstance(decision, dict):
                    pair = decision.get('currency_pair', 'UNKNOWN')
                    action = decision.get('decision', 'HOLD')
                    confidence = decision.get('confidence', 0.0)
                    reasoning = decision.get('reasoning', 'No reasoning provided')
                    
                    output.append(f"   {i}. {pair}: {action} (Confidence: {confidence:.2f})")
                    output.append(f"      Reasoning: {reasoning}")
        else:
            output.append("💰 TRADING DECISIONS: No specific trading recommendations")
        
        output.append("")
        output.append("🔗 CURRENCY PAIRS MENTIONED:")
        for pair in result["currency_pairs"]:
            output.append(f"   • {pair}")
        
        output.append("")
        output.append("=" * 60)
        
        return "\n".join(output)

class TradingCLI:
    """Interactive CLI for the integrated trading system"""
    
    def __init__(self):
        self.system = IntegratedTradingSystem()
        
    def start(self):
        """Start the interactive CLI"""
        print("🚀 Initializing Integrated RAG + Agentic AI Trading System...")
        
        if not self.system.initialize_rag_system():
            print("❌ Failed to initialize system. Exiting.")
            return
        
        print("\n" + "="*60)
        print("🤖 INTEGRATED RAG + AGENTIC AI TRADING SYSTEM")
        print("="*60)
        print("Ask questions about economic events and get trading recommendations!")
        print("Type 'exit' to quit, 'help' for examples.")
        print("="*60)
        
        while True:
            try:
                query = input("\n💬 Enter your trading question: ").strip()
                
                if query.lower() in ['exit', 'quit']:
                    print("\n👋 Goodbye!")
                    break
                
                if query.lower() == 'help':
                    self.show_examples()
                    continue
                
                if not query:
                    continue
                
                # Get trading decision
                result = self.system.get_trading_decision(query)
                
                # Display formatted result
                print("\n" + self.system.format_trading_output(result))
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def show_examples(self):
        """Show example queries"""
        examples = [
            "Non-Farm Payrolls came out higher than expected, what should I do with EUR/USD?",
            "FOMC meeting minutes showed hawkish stance, what about USD/JPY?",
            "CPI inflation data is rising, how should I trade GBP/USD?",
            "GDP growth was strong, what's the impact on USD pairs?"
        ]
        
        print("\n📝 Example Questions:")
        for i, example in enumerate(examples, 1):
            print(f"   {i}. {example}")
        print("\n💡 Tips: Be specific about economic events and currency pairs!")

# Main execution
if __name__ == "__main__":
    cli = TradingCLI()
    cli.start()
