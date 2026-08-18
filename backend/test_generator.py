"""
Standalone Generator Verification Script for PakServe AI.
Tests end-to-end RAG pipeline (Retrieval + Gemini Generation) including:
1. Procedural In-Scope Query (CNIC Renewal)
2. Out-of-Scope Query (Best pizza place in Lahore) to verify anti-hallucination refusal.
"""

import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.vector_store import query
from src.generator import generate_answer


def test_generator_pipeline():
    print("=" * 80)
    print("PakServe AI - Phase 1 Generator (Gemini RAG) Standalone Verification")
    print("=" * 80)

    # ---------------------------------------------------------
    # TEST 1: In-Scope Procedural Query
    # ---------------------------------------------------------
    query_1 = "CNIC renew karne ke liye kya chahiye"
    print("\n" + "=" * 80)
    print(f"TEST 1: In-Scope Query -> \"{query_1}\"")
    print("=" * 80)

    print("\n[Step 1] Retrieving top relevant chunks from ChromaDB...")
    chunks_1 = query(query_text=query_1, top_k=3)
    for i, c in enumerate(chunks_1, 1):
        print(f"  [{i}] Doc: {c['doc_name']} | Category: {c['category']} | Score: {c['similarity_score']:.4f}")

    print("\n[Step 2] Sending retrieved chunks + query to Gemini API (generate_answer)...")
    answer_1 = generate_answer(query_1, chunks_1)

    print("\n" + "-" * 40 + " [Generated Answer] " + "-" * 40)
    print(answer_1)
    print("-" * 100)

    # ---------------------------------------------------------
    # TEST 2: Out-of-Scope Anti-Hallucination Query
    # ---------------------------------------------------------
    query_2 = "What's the best pizza place in Lahore?"
    print("\n" + "=" * 80)
    print(f"TEST 2: Out-of-Scope Query -> \"{query_2}\"")
    print("=" * 80)

    print("\n[Step 1] Retrieving top chunks from ChromaDB (expected low semantic relevance)...")
    chunks_2 = query(query_text=query_2, top_k=3)
    for i, c in enumerate(chunks_2, 1):
        print(f"  [{i}] Doc: {c['doc_name']} | Category: {c['category']} | Score: {c['similarity_score']:.4f}")

    print("\n[Step 2] Sending retrieved chunks + query to Gemini API...")
    answer_2 = generate_answer(query_2, chunks_2)

    print("\n" + "-" * 40 + " [Generated Answer] " + "-" * 40)
    print(answer_2)
    print("-" * 100)

    print("\n" + "=" * 80)
    print("Generator Verification Complete!")
    print("=" * 80)


if __name__ == "__main__":
    test_generator_pipeline()
