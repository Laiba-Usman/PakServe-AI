"""
Standalone Retrieval Verification Script for PakServe AI.
Tests ChromaDB persistent vector retrieval with a sample natural language query.
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.vector_store import query, list_documents


def run_verification():
    print("=" * 70)
    print("PakServe AI - Phase 1 Vector Store Standalone Retrieval Test")
    print("=" * 70)

    # 1. Inspect Document Inventory
    docs = list_documents()
    print(f"\n[1] Inventory Check: {len(docs)} Unique Documents Ingested in ChromaDB:")
    categories = {}
    for d in docs:
        cat = d["category"]
        categories[cat] = categories.get(cat, 0) + d["chunk_count"]
    
    for cat, total_chunks in sorted(categories.items()):
        print(f"    - Category: {cat:<22} -> {total_chunks} chunks")

    # 2. Execute Sample Test Query
    sample_query = "CNIC renew karne ke liye kya chahiye"
    print("\n" + "=" * 70)
    print(f"[2] Executing Standalone Semantic Search Query:")
    print(f"    Query: \"{sample_query}\"")
    print(f"    Top K: 3")
    print("=" * 70)

    results = query(query_text=sample_query, top_k=3)

    if not results:
        print("ERROR: No results returned from vector store!")
        return

    for idx, res in enumerate(results, 1):
        print(f"\n--- Result #{idx} ---")
        print(f"Document Name   : {res['doc_name']}")
        print(f"Category        : {res['category']}")
        print(f"Chunk ID        : {res['chunk_id']}")
        print(f"Similarity Score: {res['similarity_score']:.4f}")
        print(f"Cosine Distance : {res['distance']:.4f}")
        print("Retrieved Content Preview:")
        # Indent and show first 300 chars of chunk text
        clean_text = "\n".join("    " + line for line in res["text"].split("\n")[:10])
        print(clean_text)
        print("    ...")

    # 3. Category-filtered Query Test
    print("\n" + "=" * 70)
    filter_query = "driving license learner permit test rules"
    print(f"[3] Executing Filtered Search Query:")
    print(f"    Query: \"{filter_query}\"")
    print(f"    Filter: {{'category': 'Driving License'}}")
    print("=" * 70)

    filtered_results = query(query_text=filter_query, top_k=2, filter={"category": "Driving License"})
    for idx, res in enumerate(filtered_results, 1):
        print(f"\n--- Filtered Result #{idx} ---")
        print(f"Document Name   : {res['doc_name']}")
        print(f"Category        : {res['category']}")
        print(f"Similarity Score: {res['similarity_score']:.4f}")
        first_few_lines = "\n".join("    " + line for line in res["text"].split("\n")[:6])
        print(first_few_lines)

    print("\n" + "=" * 70)
    print("Standalone Retrieval Pipeline Verified Successfully!")
    print("=" * 70)


if __name__ == "__main__":
    run_verification()
