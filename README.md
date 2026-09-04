# AI Document Assistant

A full-stack document Q&A assistant: upload documents, ask questions, get grounded answers with citations. Built as a portfolio project to demonstrate AI engineering skills at the application layer — RAG, agentic tool use, eval design, cost/observability — on top of an existing full-stack background.

**Request lifecycle (chat message):**
1. User sends a question in the chat UI.
2. Backend embeds the question and runs a similarity search against the vector store for the top-k relevant chunks.
3. Backend constructs a prompt: system instructions + retrieved chunks (marked as untrusted reference data) + recent conversation history + the question.
4. Backend calls the LLM with the `create_task` tool defined and available.
5. If the model has enough grounded context, it answers directly with citations. If not, it may invoke `create_task` to flag a follow-up.
6. Response streams back to the frontend; citations render inline; token count, latency, and cost are logged.
 
**Request lifecycle (document upload):**
1. User uploads a document.
2. Backend extracts text, chunks it (e.g., ~500-token chunks with overlap), embeds each chunk.
3. Chunks and embeddings are written to the vector store with metadata (document id, source location).


## Status

🚧 Day 1 of 7 — in progress.

## What's built so far

| Endpoint | Status | Notes |
|---|---|---|
| `GET /health` | ✅ | Basic liveness check |
| `POST /documents` | 🟡 placeholder | Accepts a file upload, returns filename + status. No processing/ingestion yet. |
| `POST /chat` | ✅ | Streams a response from Claude over SSE. No conversation history, no retrieval yet — single-turn only. |

Verified end-to-end: request → Anthropic SDK → model → token stream → SSE chunks reaching the client, confirmed via `curl -N`.

## Tech stack

| Layer | Tool | Status |
|---|---|---|
| Backend | Python + FastAPI | ✅ in use |
| LLM API | Anthropic Claude API (Python SDK) | ✅ in use |
| Frontend | React | ⏳ not started |
| Orchestration | LangGraph | ⏳ planned (Day 3, tool-calling loop) |
| RAG / ingestion | LlamaIndex | ⏳ planned (Day 2) |
| Vector database | Qdrant or Pinecone | ⏳ planned (Day 2) |
| Tool-calling standard | MCP | ⏳ planned (Day 3) |
| Evaluation | RAGAS | ⏳ planned (Day 4) |
| Observability | LangSmith | ⏳ planned (Day 5) |
| Database | Postgres (Supabase/Neon) | ⏳ planned |
| Deployment | Vercel + Modal/Render | ⏳ planned (Day 6–7) |

## Project structure

```
ai-document-assistant/
├── Makefile
├── .env                  # not committed
├── .gitignore
└── app/
    ├── main.py            # app entrypoint, health check, router registration
    ├── models/
    │   └── chat.py         # ChatRequest (Pydantic)
    └── routers/
        ├── documents.py     # POST /documents (placeholder)
        └── chat.py          # POST /chat (streaming)
```

## Setup

```bash
git clone <repo-url>
cd ai-document-assistant

python3 -m venv venv
source venv/bin/activate

pip install fastapi uvicorn anthropic python-dotenv python-multipart
```

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-...
```

Run the server:

```bash
make dev
```

This runs `uvicorn app.main:app --reload` on `http://localhost:8000`.

## Testing the chat endpoint

```bash
curl -N -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Say hello in one sentence"}'
```

The `-N` flag disables curl's own output buffering, so you can see the response arrive in chunks rather than all at once — this is what confirms streaming is actually working, not just that the endpoint returns a correct final answer.

## Roadmap

- [x] Day 1 (partial): FastAPI skeleton, placeholder upload endpoint, streaming chat endpoint via SSE
- [ ] Day 1–2: Frontend chat UI, document ingestion, retrieval wired into chat with citations
- [ ] Day 3: `create_task` tool via MCP, prompt-injection guardrails
- [ ] Day 4: Golden eval set (15–20 Q&A pairs), RAGAS scoring
- [ ] Day 5: Cost/latency logging via LangSmith, prompt caching
- [ ] Day 6–7: Polish, deploy, demo, final write-up

## Safety notes (so far)

- Retrieved content (once RAG is wired in) will be wrapped in explicit markers (`<reference_data>`) with a system-prompt instruction to treat it as data, never as instructions. This is a soft (learned) defense, not an architectural guarantee.
- The planned `create_task` tool is scoped to create-only, no update/delete, no external side effects — a hard, architectural boundary that limits worst-case impact if the soft defense above fails.
