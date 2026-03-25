#!/usr/bin/env python3
"""
Test Tesla Optimus questions against RAG system using CLI
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Add RAG_Logic to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'RAG_Logic'))

from logic import OptimizedRAGSystem
from src.loader import load_evaluation

def score_to_interpretation(score):
    """Convert numeric score to French interpretation"""
    interpretations = {
        5.0: "Très fidèle",
        4.0: "Correct",
        3.0: "Partiel",
        2.0: "Faible",
        1.0: "Incorrect",
        0.0: "Incorrect"
    }
    return interpretations.get(score, "Incorrect")

def print_score_report(results):
    """Print detailed score report in French format"""
    print("🔹 Étape 5 — Évaluation")
    print("Fonction : evaluer_reponses(source_file, results_file)")
    print("Critères")
    print("Score\tInterprétation")

    # Sort results by score
    sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)

    for i, result in enumerate(sorted_results, 1):
        score = result.get('score', 0)
        interpretation = score_to_interpretation(score)
        print(f"{score}\t{interpretation}")

    print(f"\n🔹 Étape 6 — Rapport")
    print(f"    • {len(results)} scores individuels")
    print(f"    • 1 score global")

async def test_tesla_questions():
    """Test Tesla Optimus questions against RAG system"""
    print("🚀 Testing Tesla Optimus Questions with RAG System")
    print("=" * 60)

    # Initialize RAG system
    print("🔧 Initializing RAG System...")
    rag_system = OptimizedRAGSystem()

    success = await rag_system.initialize_system()
    if not success:
        print("❌ Failed to initialize RAG system")
        return

    print("✅ RAG System initialized successfully")

    # Load Tesla evaluation questions
    print("\n📊 Loading Tesla Optimus evaluation questions...")
    eval_result = load_evaluation({'eval_dir': 'RAG_Logic/data/evaluation'})
    evaluations = eval_result['evaluations']

    tesla_eval = None
    for eval_file in evaluations:
        if 'tesla_optimus' in eval_file['file_name']:
            tesla_eval = eval_file
            break

    if not tesla_eval:
        print("❌ Tesla Optimus evaluation file not found")
        return

    questions = tesla_eval['data']
    print(f"✅ Loaded {len(questions)} Tesla Optimus questions")

    # Test each question
    print("\n🔍 Testing Questions...")
    print("-" * 40)
    results = []

    for i, q in enumerate(questions, 1):
        print(f"\n❓ Question {i}: {q['question']}")

        try:
            # Process query
            result = await rag_system.process_query(q['question'])

            # Check if answer contains expected keywords
            answer = result.get('answer', '')
            expected_keywords = q.get('expected_keywords', [])

            # Calculate score using same logic as evaluation function
            score = 0.0
            matched_keywords = []

            for keyword in expected_keywords:
                if keyword.lower() in answer.lower():
                    matched_keywords.append(keyword)

            # Use proper scoring logic (same as evaluation.py)
            if len(expected_keywords) > 0:
                match_percentage = len(matched_keywords) / len(expected_keywords)
                if match_percentage >= 1.0:  # All keywords matched
                    score = 5.0  # Très fidèle
                elif match_percentage >= 0.75:  # Most keywords matched
                    score = 4.0  # Correct
                elif match_percentage >= 0.5:  # Half keywords matched
                    score = 3.0  # Partiel
                elif match_percentage > 0:  # Some keywords matched
                    score = 2.0  # Faible
                else:  # No keywords matched
                    score = 1.0  # Incorrect

            result_data = {
                'question': q['question'],
                'expected_answer': q['answer'][0],
                'actual_answer': answer,
                'confidence': result.get('confidence_score', 0.0),
                'difficulty': q['difficulty'],
                'expected_keywords': expected_keywords,
                'matched_keywords': matched_keywords,
                'score': score,
                'interpretation': score_to_interpretation(score)
            }

            results.append(result_data)

            # Print result
            print(f"📝 Expected: {q['answer'][0][:100]}...")
            print(f"💡 Actual: {answer[:100]}...")
            print(f"🎯 Keywords matched: {len(matched_keywords)}/{len(expected_keywords)}")
            print(f"📈 Score: {score} ({score_to_interpretation(score)})")
            print(f"🔋 Confidence: {result.get('confidence_score', 0.0):.2f}")

        except Exception as e:
            print(f"❌ Error processing question: {str(e)}")
            error_result = {
                'question': q['question'],
                'error': str(e),
                'score': 0.0,
                'interpretation': 'Incorrect'
            }
            results.append(error_result)

    print("\n" + "=" * 60)

    # Print detailed report
    print_score_report(results)

    # Calculate statistics
    scores = [r.get('score', 0) for r in results if 'score' in r]
    successful = sum(1 for s in scores if s >= 3.0)  # Partiel or better
    total = len(scores)

    print(f"\n📊 Statistiques Générales:")
    print(f"   • Questions traitées: {total}")
    print(f"   • Réponses réussies: {successful}")
    print(f"   • Taux de réussite: {(successful/total)*100:.1f}%")
    print(f"   • Score moyen: {sum(scores)/len(scores):.2f}")

    # Save results
    output_file = "RAG_Logic/results/tesla_test_results.json"
    Path("RAG_Logic/results").mkdir(exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': str(Path.cwd()),
            'total_questions': total,
            'successful_responses': successful,
            'success_rate': (successful/total)*100,
            'average_score': sum(scores)/len(scores) if scores else 0.0,
            'interpretation': score_to_interpretation(sum(scores)/len(scores) if scores else 0.0),
            'results': results
        }, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Résultats sauvegardés dans: {output_file}")
    print("\n🎉 Test complété!")

if __name__ == "__main__":
    asyncio.run(test_tesla_questions())
