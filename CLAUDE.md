# CLAUDE.md — PakServe AI (RAG-Powered Government Services Assistant)

## Project Overview
Build a full RAG (Retrieval-Augmented Generation) chatbot that helps users navigate confusing, scattered Pakistani government service procedures (NADRA, Passport, Driving License, FBR Tax, Vehicle Registration, etc.) through natural language conversation, instead of manually searching multiple government websites/offices.

This fulfills an internship capstone assignment requiring a real-world AI solution that demonstrates: Generative AI & LLMs, Prompt Engineering, LLM APIs (Gemini), Embeddings, Vector Databases, Semantic Search, and RAG.

**Domain chosen:** Pakistani Government Services (NADRA, Passport, Driving License, FBR, Vehicle Registration, Misc civil documents)
**Core requirement:** chunk documents → generate embeddings → store in ChromaDB → accept natural language query → semantic retrieval of top relevant chunks → pass chunks as context to Gemini API → Gemini generates a clear, conversational, grounded answer → display answer + sources (doc name, category, similarity score).

**Key differentiator from a basic search tool:** This is NOT just a search-and-display app. It is a true RAG chatbot — retrieved chunks are grounded context fed to an LLM (Gemini) which synthesizes a natural, easy-to-understand answer, citing which official process/document it came from. This prevents hallucination (answers are grounded in real documents) while still feeling like a conversation, not a search engine.

**UI Requirement — IMPORTANT:** This project does **NOT** use Streamlit. Streamlit's default component styling looks generic/templated, and the goal is a polished, custom-designed, fully owned UI (chat-style, similar in spirit to a modern product like ChatGPT/Claude's own interface, but with its own distinct visual identity). The backend is a standalone REST API (FastAPI); the frontend is a separately built React app that consumes it. Frontend must NOT use default/unstyled component libraries — see Design Direction below.

---

## Real-World Problem Statement
Pakistani citizens routinely need to complete government processes — renewing a CNIC, applying for a passport, registering a vehicle, filing taxes — but the required documents, fees, eligibility rules, and steps are scattered across different websites (NADRA, DGIP, FBR, Excise & Taxation) and often written in dense bureaucratic language. This causes wasted trips to offices, missed documents, and confusion about fees/timelines. PakServe AI consolidates this information into one place and lets users ask questions in plain natural language (English or Roman Urdu) and get a clear, accurate, conversational answer grounded in real procedural information.

---

## Tech Stack

### Backend
- Python 3.10+
- FastAPI (REST API server, replaces Streamlit entirely)
- Uvicorn (ASGI server)
- ChromaDB (persistent local vector store)
- sentence-transformers (`all-MiniLM-L6-v2` model) for embeddings
- Google Gemini API (`google-genai` SDK, `genai.Client`) for answer generation — **use the new SDK, NOT the deprecated `google-generativeai` package**
- python-dotenv for API key management
- pandas (for analytics aggregation)

### Frontend
- React (Vite as the build tool — fast dev server, no unnecessary boilerplate)
- Plain CSS (custom-written, no Bootstrap/Material UI/default component kits — see Design Direction) or Tailwind utility classes if preferred for speed, but with a fully custom theme (no default Tailwind look)
- fetch/axios for calling the FastAPI backend
- Deployed/run separately from backend during development (Vite dev server + FastAPI on different ports, connected via CORS)

### Tooling
- Git & GitHub for version control

---

## Design Direction (for the React UI)
- Chat-style primary interface — message bubbles for user query and AI response, NOT a plain search bar + results list.
- Distinct visual identity: pick a theme that fits "Pakistani government services made simple" — e.g. a clean, trustworthy palette (deep green/white nod to Pakistani civic identity, or a modern neutral + single accent color), good typography, generous spacing. Avoid generic AI-app blue-gradient-robot clichés.
- Each AI answer bubble has an expandable/collapsible "Sources" section beneath it showing retrieved chunks (doc name, category, similarity score) — this must be visually secondary/subtle (e.g. small collapsed toggle) so the primary conversation stays clean.
- Sidebar or top nav for switching between: Chat (primary), Upload Document, Manage Documents, Analytics Dashboard.
- Analytics dashboard uses real charts (e.g. a lightweight charting lib like recharts) — not default browser tables.
- Fully responsive — should look good on both desktop (main demo context) and mobile.
- Loading states matter: show a typing/thinking indicator while retrieval + generation is happening (this is a multi-second operation — embedding + ChromaDB query + Gemini API call).

---

## Folder Structure

```
pakserve-ai/
│
├── backend/
│   ├── data/
│   │   └── documents/                  # 24 .txt files (raw knowledge base)
│   │       ├── nadra_cnic_new.txt
│   │       ├── nadra_cnic_renewal.txt
│   │       ├── nadra_cnic_correction.txt
│   │       ├── nadra_child_registration.txt
│   │       ├── nadra_family_registration.txt
│   │       ├── passport_fresh.txt
│   │       ├── passport_renewal.txt
│   │       ├── passport_lost.txt
│   │       ├── passport_urgent_fee_guide.txt
│   │       ├── driving_license_learner_permit.txt
│   │       ├── driving_license_new.txt
│   │       ├── driving_license_renewal.txt
│   │       ├── driving_license_international_permit.txt
│   │       ├── fbr_ntn_registration.txt
│   │       ├── fbr_tax_filing_salaried.txt
│   │       ├── fbr_tax_filing_business.txt
│   │       ├── fbr_late_filing_penalties.txt
│   │       ├── vehicle_registration_new.txt
│   │       ├── vehicle_ownership_transfer.txt
│   │       ├── vehicle_number_plate.txt
│   │       ├── domicile_certificate.txt
│   │       ├── birth_certificate.txt
│   │       ├── marriage_registration.txt
│   │       └── general_govt_faqs.txt
│   │
│   ├── chroma_db/                      # ChromaDB persistent storage (auto-generated, gitignored)
│   │
│   ├── src/
│   │   ├── __init__.py
│   │   ├── chunker.py                  # Splits documents into overlapping chunks
│   │   ├── embedder.py                 # Generates embeddings via sentence-transformers
│   │   ├── vector_store.py             # ChromaDB add/query/delete interface
│   │   ├── ingest.py                   # One-time script: reads all docs → chunk → embed → store
│   │   ├── generator.py                # Sends retrieved chunks + query to Gemini API, returns generated answer
│   │   └── analytics.py                # Logs and aggregates search history
│   │
│   ├── main.py                          # FastAPI app — defines all API endpoints
│   ├── .env                              # GEMINI_API_KEY (gitignored, never committed)
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatWindow.jsx           # Main chat message list + input box
│   │   │   ├── MessageBubble.jsx        # Single message (user or AI), AI includes SourcesPanel
│   │   │   ├── SourcesPanel.jsx         # Collapsible retrieved-chunks display
│   │   │   ├── Sidebar.jsx              # Nav between Chat / Upload / Manage / Analytics
│   │   │   ├── UploadPanel.jsx          # Bonus: upload new doc
│   │   │   ├── ManagePanel.jsx          # Bonus: list + delete docs
│   │   │   └── AnalyticsPanel.jsx       # Bonus: charts (recharts)
│   │   ├── api/
│   │   │   └── client.js                # fetch/axios wrapper for calling FastAPI backend
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles/                      # custom CSS (theme variables, component styles)
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── README.md
└── .gitignore
```

---

## Metadata Schema
Every chunk stored in ChromaDB must carry this metadata so the **metadata filter** bonus feature and source citation work:

```python
metadata = {
    "doc_name": "nadra_cnic_renewal.txt",
    "category": "NADRA",
    "chunk_id": 3
}
```

### Category Mapping
| Category | Documents |
|---|---|
| NADRA | CNIC New, CNIC Renewal, CNIC Correction, Child Registration Certificate, Family Registration Certificate |
| Passport | Fresh Passport, Renewal, Lost Passport, Urgent/Normal Fee Guide |
| Driving License | Learner Permit, New License, Renewal, International Driving Permit |
| Tax (FBR) | NTN Registration, Tax Filing (Salaried), Tax Filing (Business), Late Filing Penalties |
| Vehicle Registration | New Vehicle Registration, Ownership Transfer, Number Plate |
| Civil Documents | Domicile Certificate, Birth Certificate, Marriage Registration |
| General | General Govt FAQs (fees overview, office timings, helpline numbers) |

---

## API Endpoints (FastAPI — `backend/main.py`)

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/chat` | Body: `{ query: str, category_filter?: str }`. Runs full RAG pipeline (embed → retrieve → generate). Returns `{ answer: str, sources: [{ text, doc_name, category, chunk_id, similarity_score }] }` |
| POST | `/api/documents/upload` | Multipart file upload (`.txt`). Chunks, embeds, and stores the new doc. Returns confirmation + chunk count. |
| GET | `/api/documents` | Returns list of all ingested documents with metadata (name, category, chunk count). |
| DELETE | `/api/documents/{doc_name}` | Deletes all chunks belonging to a document from ChromaDB. |
| GET | `/api/analytics` | Returns aggregate stats: total searches, top queries, category-wise usage, most-retrieved documents. |

CORS must be enabled on the FastAPI app (`fastapi.middleware.cors.CORSMiddleware`) to allow requests from the Vite dev server origin (e.g. `http://localhost:5173`).

---

## Module Responsibilities

### `backend/src/chunker.py`
- `chunk_text(text, chunk_size=300, overlap=50)`
- Splits each document into overlapping chunks (word-based) so context isn't lost at chunk boundaries.

### `backend/src/embedder.py`
- Loads `sentence-transformers` model `all-MiniLM-L6-v2`.
- `get_embedding(text)` → returns a vector for a given chunk or query.

### `backend/src/vector_store.py`
- Sets up a persistent ChromaDB client (`chroma_db/` directory).
- `add_documents(chunks, embeddings, metadata)`
- `query(query_text, top_k=5, filter=None)` — supports optional metadata filter (e.g. by category).
- `delete_document(doc_name)`
- `list_documents()` — for the Manage panel / GET `/api/documents`.

### `backend/src/ingest.py`
- One-time / re-runnable script.
- Reads all `.txt` files from `data/documents/`, chunks them, embeds them, and stores them in ChromaDB with metadata.

### `backend/src/generator.py`
- Loads `GEMINI_API_KEY` from `.env` using `python-dotenv`.
- Uses `google-genai` SDK (`from google import genai`, `client = genai.Client()`).
- `generate_answer(user_query, retrieved_chunks)`:
  - Builds a prompt that includes the user's question + the retrieved chunk texts as grounding context.
  - System instruction must explicitly tell Gemini: **"Only answer based on the provided context. If the context does not contain the answer, say you don't have verified information on that and recommend checking the official source. Do not invent fees, document lists, or timelines that are not in the context."**
  - Returns a natural, conversational answer string, ideally referencing which process/category it drew from.
- This grounding instruction is critical — it prevents hallucination of fees/requirements.

### `backend/src/analytics.py`
- Logs every search query (query text, timestamp, top result, category) to a CSV or JSON file (or a separate ChromaDB collection).
- Provides aggregate stats consumed by GET `/api/analytics`.

### `backend/main.py`
- FastAPI app instance, CORS middleware, all endpoints from the API table above, wiring together embedder → vector_store → generator → analytics.

### Frontend components (`frontend/src/components/`)
- **ChatWindow.jsx** — holds message state, input box, send button, calls `/api/chat`, shows typing indicator while awaiting response.
- **MessageBubble.jsx** — renders one message; if it's an AI message, renders `SourcesPanel` beneath it.
- **SourcesPanel.jsx** — collapsed by default, expands to show retrieved chunk text/doc name/category/score.
- **Sidebar.jsx** — navigation between Chat / Upload / Manage / Analytics views.
- **UploadPanel.jsx** — file input, calls `/api/documents/upload`, shows success/chunk count.
- **ManagePanel.jsx** — lists documents from `/api/documents`, delete button calling `/api/documents/{doc_name}`.
- **AnalyticsPanel.jsx** — fetches `/api/analytics`, renders charts with recharts (bar chart for top queries/categories, etc.).

---

## Data Flow

```
[documents/*.txt] → chunker.py → [chunks] → embedder.py → [vectors]
                                                              ↓
                                                   vector_store.py (ChromaDB)
                                                              ↓
React ChatWindow → POST /api/chat → main.py
                                       ↓
                            embedder.py (embed query)
                                       ↓
                            vector_store.query() → top 3–5 chunks
                                       ↓
                            generator.py (chunks + query → Gemini API)
                                       ↓
                     { answer, sources } → JSON response → React renders
                     MessageBubble (answer) + SourcesPanel (sources)
```

---

## Assignment Requirements Checklist
- [ ] Real-world problem clearly identified (govt service navigation confusion)
- [ ] 20–30 knowledge base documents (24 chosen, categorized above)
- [ ] Documents split into chunks
- [ ] Embeddings generated (sentence-transformers)
- [ ] Embeddings stored in ChromaDB (persistent)
- [ ] Semantic search retrieval working (top 3–5 relevant chunks)
- [ ] Gemini API integration for grounded answer generation (RAG, not just retrieval)
- [ ] Anti-hallucination system prompt in generator.py
- [ ] Custom React chat UI (NOT Streamlit) displaying: generated answer, retrieved source text, similarity score, document name, metadata
- [ ] FastAPI backend exposing clean REST endpoints, CORS configured
- [ ] Bonus: upload new documents (via UI)
- [ ] Bonus: delete documents (via UI)
- [ ] Bonus: filter by metadata (category)
- [ ] Bonus: search analytics dashboard (with real charts)
- [ ] Git & GitHub used for version control, with meaningful commits
- [ ] README.md with setup + run instructions (backend AND frontend, since they run separately) + problem/solution explanation
- [ ] 5-minute presentation prepared (title, problem, solution, tech used, features, improvements, demo, future work)

---

## Build Order (recommended sequence for the agent)

**Phase 1 — Backend core pipeline (no API, no frontend yet)**
1. Scaffold `backend/` folder structure and `backend/requirements.txt`.
2. Write `backend/src/chunker.py` + quick unit test on one sample doc.
3. Write `backend/src/embedder.py` + verify embedding shape/output.
4. Write `backend/src/vector_store.py` with ChromaDB add/query/delete/list.
5. Write `backend/src/ingest.py`, populate `backend/data/documents/` with all 24 `.txt` files (realistic content based on real Pakistani government procedures — NADRA, Passport/DGIP, Excise & Taxation, FBR, vehicle registration — a few hundred to ~1000 words each). Run ingestion, verify ChromaDB persists.
6. Verify retrieval works standalone: run a sample query directly against `vector_store.py`, print top 3 results with similarity scores.
7. Write `backend/src/generator.py` — Gemini integration with the anti-hallucination system prompt. Test standalone with a query + retrieved chunks; confirm grounded, non-hallucinated output.

**Phase 2 — FastAPI backend**
8. Write `backend/main.py` with all endpoints from the API table. Test each endpoint with a tool like curl/Postman/FastAPI's own `/docs` Swagger UI before touching the frontend.
9. Write `backend/src/analytics.py` and wire logging into `/api/chat`, implement `/api/analytics`.

**Phase 3 — React frontend**
10. Scaffold `frontend/` with Vite + React.
11. Build the custom theme/design system first (CSS variables: colors, spacing, typography) per the Design Direction section — before building components, so everything is visually consistent from the start.
12. Build `ChatWindow.jsx` + `MessageBubble.jsx` + `SourcesPanel.jsx`, wire to `/api/chat`. Confirm end-to-end: query "CNIC renew karne ke liye kya chahiye?" surfaces the NADRA CNIC renewal doc and Gemini generates a grounded answer, sources visible in collapsible panel.
13. Build `Sidebar.jsx` navigation, then `UploadPanel.jsx`, `ManagePanel.jsx`, `AnalyticsPanel.jsx` (bonus features), wiring each to its endpoint.
14. Polish: loading/typing indicators, responsive layout check, empty states, error states (e.g. backend unreachable).

**Phase 4 — Wrap-up**
15. Write root `README.md` — problem statement, proposed solution, tech stack, setup/run instructions for BOTH backend and frontend (they start separately), and a short "how RAG grounding prevents hallucination" note.
16. Add `.gitignore` (exclude `chroma_db/`, `.env`, `__pycache__/`, `node_modules/`, `dist/`, venv, etc.), init git repo, commit incrementally through the phases above (not one giant commit at the end).

## Notes for the Agent
- Keep all comments/docstrings in English for portability, even though planning notes were in Hindi/Urdu (Roman script).
- Use `all-MiniLM-L6-v2` for embeddings — small, fast, sufficient for this scale (no GPU required).
- Use the **new** `google-genai` SDK (`from google import genai`, `genai.Client()`) — the old `google-generativeai` package is deprecated. Use a current Gemini flash-tier model for speed/cost.
- Never hardcode the Gemini API key — always load from `.env` via `python-dotenv`, and ensure `.env` is in `.gitignore`.
- Do NOT use Streamlit anywhere in this project. Do NOT default to an unstyled/default-look component library on the frontend — the whole point of this architecture choice is a custom, deliberately designed UI.
- Backend and frontend run as two separate processes during development (`uvicorn main:app --reload` and `npm run dev`). Document both startup commands clearly in the README.
- The anti-hallucination system prompt in `generator.py` is the single most important backend piece — it's what makes this a defensible, demo-safe RAG system instead of a generic LLM wrapper that might invent fees or document requirements.
- Prioritize correctness of the core pipeline (chunk → embed → store → retrieve → generate) before building the frontend, and prioritize the frontend's core chat flow before bonus panels.
- Each `.txt` file in `data/documents/` should reflect realistic, generally accurate Pakistani government procedures. It's acceptable to note in the README that content is illustrative/for demo purposes and users should verify with official sources for actual transactions — this also honestly addresses the "Limitations" a judge might ask about.
