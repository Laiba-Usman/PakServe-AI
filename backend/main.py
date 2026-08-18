"""
PakServe AI - FastAPI REST API Backend
Provides endpoints for conversational RAG queries, document management,
and search analytics for Pakistani civic procedures.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure backend root is on sys.path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.chunker import chunk_text
from src.embedder import get_embedding
from src.vector_store import add_documents, delete_document, list_documents, query
from src.generator import generate_answer
from src.analytics import get_analytics, log_search
from src.ingest import get_category_for_file

# Initialize FastAPI App
app = FastAPI(
    title="PakServe AI API",
    description="RAG-powered conversational assistant for Pakistani government services",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for React Vite Frontend (http://localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOCUMENTS_DIR = BACKEND_DIR / "data" / "documents"
os.makedirs(DOCUMENTS_DIR, exist_ok=True)


# --------------------------------------------------------------------------
# Request & Response Models
# --------------------------------------------------------------------------

class ChatRequest(BaseModel):
    query: str = Field(..., description="User's natural language question", min_length=1)
    category_filter: Optional[str] = Field(None, description="Optional category filter (e.g. 'NADRA', 'Passport')")


class SourceItem(BaseModel):
    text: str
    doc_name: str
    category: str
    chunk_id: int
    similarity_score: float


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceItem]


class DocumentSummary(BaseModel):
    doc_name: str
    category: str
    chunk_count: int


# --------------------------------------------------------------------------
# API Endpoints
# --------------------------------------------------------------------------

@app.get("/", tags=["Health"])
def root():
    """Root health check endpoint."""
    return {
        "status": "PakServe AI backend running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
def chat(request: ChatRequest):
    """
    Execute full RAG pipeline:
    1. Embed query
    2. Retrieve top relevant chunks from ChromaDB (with optional category filter)
    3. Generate grounded answer via Gemini API
    4. Log query in analytics
    5. Return generated response with citation sources
    """
    user_query = request.query.strip()
    if not user_query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query cannot be empty.")

    # Build filter if provided
    metadata_filter = None
    if request.category_filter and request.category_filter.strip():
        metadata_filter = {"category": request.category_filter.strip()}

    # 1 & 2. Retrieve chunks from vector store
    retrieved_chunks = query(query_text=user_query, top_k=5, filter=metadata_filter)

    # 3. Generate grounded answer
    answer = generate_answer(user_query=user_query, retrieved_chunks=retrieved_chunks)

    # 4. Log search event for analytics
    top_doc = retrieved_chunks[0]["doc_name"] if retrieved_chunks else "None"
    top_cat = retrieved_chunks[0]["category"] if retrieved_chunks else (request.category_filter or "General")
    log_search(query=user_query, top_result_doc=top_doc, category=top_cat)

    # 5. Format response sources
    sources = [
        SourceItem(
            text=c.get("text", ""),
            doc_name=c.get("doc_name", "Unknown"),
            category=c.get("category", "General"),
            chunk_id=int(c.get("chunk_id", 0)),
            similarity_score=float(c.get("similarity_score", 0.0))
        )
        for c in retrieved_chunks
    ]

    return ChatResponse(answer=answer, sources=sources)


@app.post("/api/documents/upload", tags=["Documents"])
async def upload_document(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None)
):
    """
    Upload and index a new .txt document into the knowledge base:
    1. Reads and validates text content
    2. Chunks text via chunker.py
    3. Generates embeddings via embedder.py
    4. Stores chunks with metadata in ChromaDB
    5. Saves copy in backend/data/documents/
    """
    if not file.filename.endswith(".txt"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only plain text (.txt) files are supported."
        )

    try:
        content_bytes = await file.read()
        text_content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be valid UTF-8 encoded text."
        )

    if not text_content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    # Determine category
    final_category = category.strip() if (category and category.strip()) else get_category_for_file(file.filename)

    # Chunk text
    chunks = chunk_text(text_content, chunk_size=300, overlap=50)
    if not chunks:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No chunks could be extracted.")

    # Generate embeddings
    embeddings = get_embedding(chunks)

    # Build metadatas
    metadatas = [
        {
            "doc_name": file.filename,
            "category": final_category,
            "chunk_id": i
        }
        for i in range(len(chunks))
    ]

    # Save to ChromaDB
    add_documents(chunks=chunks, embeddings=embeddings, metadata=metadatas)

    # Save copy to disk
    file_path = DOCUMENTS_DIR / file.filename
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text_content)

    return {
        "doc_name": file.filename,
        "category": final_category,
        "chunks_added": len(chunks),
        "message": f"Successfully indexed '{file.filename}' with {len(chunks)} chunks."
    }


@app.get("/api/documents", response_model=List[DocumentSummary], tags=["Documents"])
def get_documents():
    """
    Retrieve list of all ingested documents with metadata summaries
    (document name, category, and chunk count).
    """
    docs = list_documents()
    return [
        DocumentSummary(
            doc_name=d["doc_name"],
            category=d["category"],
            chunk_count=d["chunk_count"]
        )
        for d in docs
    ]


@app.delete("/api/documents/{doc_name}", tags=["Documents"])
def remove_document(doc_name: str):
    """
    Delete all chunks of a document from ChromaDB vector store.
    Also removes local file copy if present.
    """
    remaining = delete_document(doc_name=doc_name)

    # Remove file from disk if exists
    file_path = DOCUMENTS_DIR / doc_name
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            print(f"[Warning] Could not remove physical file {doc_name}: {e}")

    return {
        "doc_name": doc_name,
        "message": f"Document '{doc_name}' deleted successfully from vector database.",
        "remaining_collection_count": remaining
    }


@app.get("/api/analytics", tags=["Analytics"])
def analytics_endpoint():
    """
    Return aggregate search metrics: total searches, top queries,
    category breakdown, and most retrieved documents.
    """
    return get_analytics()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
