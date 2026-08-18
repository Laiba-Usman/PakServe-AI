"""
Automated API Verification Script for PakServe AI FastAPI backend.
Tests all endpoints:
1. GET / (Health check)
2. POST /api/chat (RAG chat with Gemini & ChromaDB)
3. POST /api/documents/upload (Upload & index new .txt document)
4. GET /api/documents (List all documents with chunk counts)
5. DELETE /api/documents/{doc_name} (Delete document from ChromaDB)
6. GET /api/analytics (Fetch search metrics & stats)
"""

import io
import json
import sys
import time
import requests

BASE_URL = "http://127.0.0.1:8000"

# Configure console encoding for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def test_all_endpoints():
    print("=" * 80)
    print("PakServe AI - FastAPI Endpoints Automated Verification Suite")
    print("=" * 80)

    # -------------------------------------------------------------
    # 1. Health Check
    # -------------------------------------------------------------
    print("\n[TEST 1] GET / (Root Health Check)")
    r = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {r.status_code}")
    print(f"Response   : {json.dumps(r.json(), indent=2)}")
    assert r.status_code == 200, "Health check failed"

    # -------------------------------------------------------------
    # 2. Chat Endpoint (In-Scope Query with Category Filter)
    # -------------------------------------------------------------
    print("\n" + "=" * 80)
    print("[TEST 2] POST /api/chat (Query with Category Filter: 'NADRA')")
    chat_payload = {
        "query": "CNIC renew karwane ki fees aur timings kya hain?",
        "category_filter": "NADRA"
    }
    print(f"Request Payload: {json.dumps(chat_payload, ensure_ascii=False)}")
    r = requests.post(f"{BASE_URL}/api/chat", json=chat_payload)
    print(f"Status Code    : {r.status_code}")
    data = r.json()
    print("\nGenerated AI Answer:")
    print("-" * 50)
    print(data.get("answer"))
    print("-" * 50)
    print(f"Retrieved Sources Count: {len(data.get('sources', []))}")
    for i, s in enumerate(data.get("sources", [])[:3], 1):
        print(f"  Source {i}: {s['doc_name']} [{s['category']}] (Score: {s['similarity_score']:.4f})")
    assert r.status_code == 200, "Chat request failed"

    # -------------------------------------------------------------
    # 3. Document Upload
    # -------------------------------------------------------------
    print("\n" + "=" * 80)
    print("[TEST 3] POST /api/documents/upload (Upload temporary document)")
    sample_content = (
        "E-Sahulat Kiosk Emergency Token Service Guide.\n"
        "Citizens can now print emergency temporary verification tokens at any NADRA e-Sahulat kiosk "
        "across Islamabad and Rawalpindi. The fee is Rs. 100 paid via cash. Processing time is instant (under 2 minutes)."
    )
    files = {
        "file": ("test_esahulat_guide.txt", io.BytesIO(sample_content.encode("utf-8")), "text/plain")
    }
    data_form = {"category": "NADRA"}
    r = requests.post(f"{BASE_URL}/api/documents/upload", files=files, data=data_form)
    print(f"Status Code: {r.status_code}")
    print(f"Response   : {json.dumps(r.json(), indent=2)}")
    assert r.status_code == 200, "Document upload failed"

    # -------------------------------------------------------------
    # 4. List Documents
    # -------------------------------------------------------------
    print("\n" + "=" * 80)
    print("[TEST 4] GET /api/documents (List all indexed documents)")
    r = requests.get(f"{BASE_URL}/api/documents")
    print(f"Status Code     : {r.status_code}")
    docs = r.json()
    print(f"Total Documents : {len(docs)}")
    uploaded_found = any(d["doc_name"] == "test_esahulat_guide.txt" for d in docs)
    print(f"Found uploaded 'test_esahulat_guide.txt' in list: {uploaded_found}")
    print("Sample document entries:")
    for d in docs[:5]:
        print(f"  - {d['doc_name']} ({d['category']}): {d['chunk_count']} chunk(s)")
    assert uploaded_found, "Uploaded document not found in /api/documents"

    # -------------------------------------------------------------
    # 5. Delete Document
    # -------------------------------------------------------------
    print("\n" + "=" * 80)
    print("[TEST 5] DELETE /api/documents/test_esahulat_guide.txt (Delete temporary document)")
    r = requests.delete(f"{BASE_URL}/api/documents/test_esahulat_guide.txt")
    print(f"Status Code: {r.status_code}")
    print(f"Response   : {json.dumps(r.json(), indent=2)}")
    assert r.status_code == 200, "Delete document failed"

    # Verify deletion in list
    r_check = requests.get(f"{BASE_URL}/api/documents")
    still_present = any(d["doc_name"] == "test_esahulat_guide.txt" for d in r_check.json())
    print(f"Document still present after deletion: {still_present}")
    assert not still_present, "Document was not properly deleted from vector store"

    # -------------------------------------------------------------
    # 6. Analytics Endpoint
    # -------------------------------------------------------------
    print("\n" + "=" * 80)
    print("[TEST 6] GET /api/analytics (Aggregate search statistics)")
    # Trigger one more chat query for richer analytics
    requests.post(f"{BASE_URL}/api/chat", json={"query": "Driving license learner permit test pattern"})
    r = requests.get(f"{BASE_URL}/api/analytics")
    print(f"Status Code: {r.status_code}")
    analytics_data = r.json()
    print(f"Total Searches           : {analytics_data.get('total_searches')}")
    print(f"Top Queries              : {json.dumps(analytics_data.get('top_queries'), indent=2)}")
    print(f"Category Breakdown       : {json.dumps(analytics_data.get('category_usage'), indent=2)}")
    print(f"Most Retrieved Documents : {json.dumps(analytics_data.get('most_retrieved_documents'), indent=2)}")
    assert analytics_data.get("total_searches", 0) >= 2, "Analytics total searches count is incorrect"

    print("\n" + "=" * 80)
    print("ALL 6 API ENDPOINTS VERIFIED AND PASSING SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    test_all_endpoints()
