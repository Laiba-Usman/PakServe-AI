/**
 * PakServe AI - API Client Wrapper
 * Connects to FastAPI backend at http://localhost:8000
 */

const API_BASE = "http://localhost:8000";

/**
 * Send natural language query to RAG Chat endpoint.
 * @param {string} query 
 * @param {string|null} categoryFilter 
 * @returns {Promise<{answer: string, sources: Array}>}
 */
export async function sendChatMessage(query, categoryFilter = null) {
  const payload = { query };
  if (categoryFilter && categoryFilter.trim() !== "" && categoryFilter !== "All") {
    payload.category_filter = categoryFilter;
  }

  const response = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: "Network request failed" }));
    throw new Error(err.detail || `Server error: ${response.status}`);
  }

  return response.json();
}

/**
 * Upload a .txt procedural document.
 * @param {File} file 
 * @param {string|null} category 
 * @returns {Promise<{doc_name: string, category: string, chunks_added: number, message: string}>}
 */
export async function uploadDocument(file, category = null) {
  const formData = new FormData();
  formData.append("file", file);
  if (category) {
    formData.append("category", category);
  }

  const response = await fetch(`${API_BASE}/api/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || `Upload failed with status ${response.status}`);
  }

  return response.json();
}

/**
 * Fetch all ingested documents with metadata and chunk counts.
 * @returns {Promise<Array<{doc_name: string, category: string, chunk_count: number}>>}
 */
export async function listDocuments() {
  const response = await fetch(`${API_BASE}/api/documents`);
  if (!response.ok) {
    throw new Error(`Failed to fetch documents: ${response.status}`);
  }
  return response.json();
}

/**
 * Delete a document and its chunks from ChromaDB.
 * @param {string} docName 
 * @returns {Promise<{doc_name: string, message: string, remaining_collection_count: number}>}
 */
export async function deleteDocument(docName) {
  const response = await fetch(`${API_BASE}/api/documents/${encodeURIComponent(docName)}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: "Delete failed" }));
    throw new Error(err.detail || `Delete failed with status ${response.status}`);
  }

  return response.json();
}

/**
 * Fetch search metrics and analytics stats.
 * @returns {Promise<{total_searches: number, top_queries: Array, category_usage: Object, most_retrieved_documents: Array}>}
 */
export async function getAnalytics() {
  const response = await fetch(`${API_BASE}/api/analytics`);
  if (!response.ok) {
    throw new Error(`Failed to fetch analytics: ${response.status}`);
  }
  return response.json();
}
