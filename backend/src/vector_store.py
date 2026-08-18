"""
Vector Store module for PakServe AI.
Manages persistent ChromaDB vector storage, document indexing, similarity search,
and document lifecycle operations with metadata filtering support.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import chromadb
from chromadb.config import Settings

from src.embedder import get_embedding

# Base paths
BACKEND_DIR = Path(__file__).resolve().parent.parent
CHROMA_DB_DIR = BACKEND_DIR / "chroma_db"
COLLECTION_NAME = "pakserve_documents"

# Ensure chroma_db directory exists
os.makedirs(CHROMA_DB_DIR, exist_ok=True)

# ChromaDB Persistent Client singleton
_chroma_client = None
_collection = None


def get_client() -> chromadb.PersistentClient:
    """
    Get or initialize persistent ChromaDB client.
    """
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(
            path=str(CHROMA_DB_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
    return _chroma_client


def get_collection():
    """
    Get or create the ChromaDB collection with cosine distance metric.
    """
    global _collection
    if _collection is None:
        client = get_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    return _collection


def add_documents(
    chunks: List[str],
    embeddings: List[List[float]],
    metadata: List[Dict[str, Any]],
    ids: Optional[List[str]] = None
) -> None:
    """
    Add or update chunks with embeddings and metadata into ChromaDB.

    Args:
        chunks (List[str]): Text contents of the chunks.
        embeddings (List[List[float]]): Vector embeddings for each chunk.
        metadata (List[Dict[str, Any]]): Metadata dicts containing doc_name, category, chunk_id.
        ids (Optional[List[str]]): Optional custom unique IDs for chunks.
    """
    if not chunks:
        return

    collection = get_collection()

    if ids is None:
        ids = [
            f"{m.get('doc_name', 'doc')}_{m.get('chunk_id', idx)}"
            for idx, m in enumerate(metadata)
        ]

    # ChromaDB accepts metadatas with primitive types (str, int, float, bool)
    clean_metadata = []
    for m in metadata:
        clean_metadata.append({
            "doc_name": str(m.get("doc_name", "")),
            "category": str(m.get("category", "")),
            "chunk_id": int(m.get("chunk_id", 0))
        })

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=clean_metadata
    )


def query(
    query_text: str,
    top_k: int = 5,
    filter: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Perform semantic search over stored chunks.

    Args:
        query_text (str): Natural language user query.
        top_k (int): Number of top relevant chunks to retrieve. Defaults to 5.
        filter (Optional[Dict[str, Any]]): Optional metadata filter dict (e.g. {"category": "NADRA"}).

    Returns:
        List[Dict[str, Any]]: List of retrieved chunk dicts with keys:
            - text (str)
            - doc_name (str)
            - category (str)
            - chunk_id (int)
            - similarity_score (float)
            - distance (float)
    """
    collection = get_collection()
    count = collection.count()
    if count == 0:
        return []

    # Adjust top_k if collection has fewer items
    n_results = min(top_k, count)

    query_embedding = get_embedding(query_text)

    query_args = {
        "query_embeddings": [query_embedding],
        "n_results": n_results,
        "include": ["documents", "metadatas", "distances"]
    }
    if filter:
        query_args["where"] = filter

    results = collection.query(**query_args)

    formatted_results: List[Dict[str, Any]] = []

    if not results or not results.get("documents") or not results["documents"][0]:
        return formatted_results

    docs = results["documents"][0]
    metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
    dists = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

    for doc, meta, dist in zip(docs, metas, dists):
        # With cosine distance: distance ranges [0, 2].
        # Cosine similarity = 1 - distance (ranges [-1, 1], typically [0, 1] for positive embeddings)
        sim_score = round(max(0.0, 1.0 - dist), 4)
        formatted_results.append({
            "text": doc,
            "doc_name": meta.get("doc_name", ""),
            "category": meta.get("category", ""),
            "chunk_id": meta.get("chunk_id", 0),
            "similarity_score": sim_score,
            "distance": round(dist, 4)
        })

    return formatted_results


def delete_document(doc_name: str) -> int:
    """
    Delete all chunks belonging to a document by doc_name.

    Args:
        doc_name (str): The filename/document identifier to delete.

    Returns:
        int: Total items remaining in collection after deletion.
    """
    collection = get_collection()
    collection.delete(where={"doc_name": doc_name})
    return collection.count()


def list_documents() -> List[Dict[str, Any]]:
    """
    List all ingested unique documents with metadata summaries (name, category, chunk count).

    Returns:
        List[Dict[str, Any]]: Aggregated document metadata summary.
    """
    collection = get_collection()
    all_data = collection.get(include=["metadatas"])

    doc_map: Dict[str, Dict[str, Any]] = {}

    if all_data and all_data.get("metadatas"):
        for meta in all_data["metadatas"]:
            doc_name = meta.get("doc_name", "Unknown")
            category = meta.get("category", "General")
            if doc_name not in doc_map:
                doc_map[doc_name] = {
                    "doc_name": doc_name,
                    "category": category,
                    "chunk_count": 0
                }
            doc_map[doc_name]["chunk_count"] += 1

    return sorted(list(doc_map.values()), key=lambda x: (x["category"], x["doc_name"]))
