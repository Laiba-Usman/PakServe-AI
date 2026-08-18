"""
Ingestion script for PakServe AI.
Reads all knowledge base documents from backend/data/documents/,
splits them into overlapping chunks using chunker.py,
generates embeddings using embedder.py,
and populates the persistent ChromaDB vector store.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List

# Ensure backend directory is on Python path
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.chunker import chunk_text
from src.embedder import get_embedding
from src.vector_store import add_documents, get_collection, list_documents

DOCUMENTS_DIR = BACKEND_DIR / "data" / "documents"

# Explicit category mapping according to CLAUDE.md spec
CATEGORY_MAP: Dict[str, str] = {
    # NADRA
    "nadra_cnic_new.txt": "NADRA",
    "nadra_cnic_renewal.txt": "NADRA",
    "nadra_cnic_correction.txt": "NADRA",
    "nadra_child_registration.txt": "NADRA",
    "nadra_family_registration.txt": "NADRA",
    # Passport
    "passport_fresh.txt": "Passport",
    "passport_renewal.txt": "Passport",
    "passport_lost.txt": "Passport",
    "passport_urgent_fee_guide.txt": "Passport",
    # Driving License
    "driving_license_learner_permit.txt": "Driving License",
    "driving_license_new.txt": "Driving License",
    "driving_license_renewal.txt": "Driving License",
    "driving_license_international_permit.txt": "Driving License",
    # Tax (FBR)
    "fbr_ntn_registration.txt": "Tax (FBR)",
    "fbr_tax_filing_salaried.txt": "Tax (FBR)",
    "fbr_tax_filing_business.txt": "Tax (FBR)",
    "fbr_late_filing_penalties.txt": "Tax (FBR)",
    # Vehicle Registration
    "vehicle_registration_new.txt": "Vehicle Registration",
    "vehicle_ownership_transfer.txt": "Vehicle Registration",
    "vehicle_number_plate.txt": "Vehicle Registration",
    # Civil Documents
    "domicile_certificate.txt": "Civil Documents",
    "birth_certificate.txt": "Civil Documents",
    "marriage_registration.txt": "Civil Documents",
    # General
    "general_govt_faqs.txt": "General",
}


def get_category_for_file(filename: str) -> str:
    """Determine document category from mapping or filename heuristics."""
    if filename in CATEGORY_MAP:
        return CATEGORY_MAP[filename]
    name_lower = filename.lower()
    if "nadra" in name_lower or "cnic" in name_lower:
        return "NADRA"
    if "passport" in name_lower:
        return "Passport"
    if "driving" in name_lower or "license" in name_lower:
        return "Driving License"
    if "fbr" in name_lower or "tax" in name_lower or "ntn" in name_lower:
        return "Tax (FBR)"
    if "vehicle" in name_lower:
        return "Vehicle Registration"
    if "domicile" in name_lower or "birth" in name_lower or "marriage" in name_lower:
        return "Civil Documents"
    return "General"


def ingest_all_documents(documents_dir: Path = DOCUMENTS_DIR) -> Dict[str, int]:
    """
    Ingest all .txt files from documents_dir into ChromaDB.

    Returns:
        Dict[str, int]: Ingestion summary statistics.
    """
    if not documents_dir.exists():
        raise FileNotFoundError(f"Documents directory not found at: {documents_dir}")

    txt_files = sorted(list(documents_dir.glob("*.txt")))
    if not txt_files:
        print(f"No .txt files found in {documents_dir}")
        return {"documents_processed": 0, "total_chunks": 0}

    print(f"Starting ingestion of {len(txt_files)} documents from {documents_dir}...")

    all_chunks: List[str] = []
    all_metadatas: List[Dict[str, any]] = []

    for file_path in txt_files:
        doc_name = file_path.name
        category = get_category_for_file(doc_name)

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_text(text, chunk_size=300, overlap=50)
        print(f"  - [{category}] {doc_name}: {len(chunks)} chunks")

        for idx, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadatas.append({
                "doc_name": doc_name,
                "category": category,
                "chunk_id": idx
            })

    print(f"\nGenerating vector embeddings for {len(all_chunks)} chunks via sentence-transformers (all-MiniLM-L6-v2)...")
    embeddings = get_embedding(all_chunks)

    print(f"Storing chunks and embeddings in persistent ChromaDB collection...")
    add_documents(chunks=all_chunks, embeddings=embeddings, metadata=all_metadatas)

    collection = get_collection()
    total_stored = collection.count()

    print(f"\nIngestion Complete!")
    print(f"  - Total Documents Ingested: {len(txt_files)}")
    print(f"  - Total Chunks Stored: {len(all_chunks)}")
    print(f"  - ChromaDB Collection Size: {total_stored} chunks")

    return {
        "documents_processed": len(txt_files),
        "total_chunks": len(all_chunks),
        "collection_total": total_stored
    }


if __name__ == "__main__":
    ingest_all_documents()
