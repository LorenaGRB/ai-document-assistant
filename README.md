# AI Document Assistant

A full-stack document Q&A assistant: upload documents, ask questions, get grounded answers with citations. Built as a portfolio project to demonstrate AI engineering skills at the application layer (RAG, agentic tool use, eval design, cost/observability) on top of an existing full-stack background.

## Status

Ingestion and retrieval are done: chat answers are grounded in the uploaded documents, and the frontend runs on real document data. Chat history persistence is in progress (the `messages` schema is defined; the repository adapter and the chat wiring are pending), and the `create_task` agent tool comes right after. Full design, decisions and audit: [docs/Project_description_v2.md](docs/Project_description_v2.md).

| Area | Status | Notes |
| --- | --- | --- |
| `GET /health` | ✅ | Liveness check |
| `POST /documents` | ✅ | Validates type (PDF/text), rejects duplicate filenames (409), stores the file, and starts background processing |
| `GET /documents` | ✅ | Lists documents, newest first |
| `GET /documents/{id}/status` | ✅ | Streams `processed` or `failed` (bare status string with an event-stream content type, no SSE framing; read it with `fetch`, not `EventSource`) |
| `POST /chat` | 🟡 | Streams a Claude response grounded in retrieved chunks. Single-turn: no history, no `conversation_id` |
| Ingestion pipeline | ✅ | Extract → chunk → embed → upsert to Pinecone → update status |
| Retrieval | ✅ | Top-k (5) cosine search, filtered by `min_score=0.3` (not yet validated against real questions) |
| Citations | ⏳ | Chunks are labelled `[filename, chunk index N]` in the prompt, but the backend does not send them to the client; the UI shell exists |
| Message history (`messages` table) | 🟡 | In progress, required for the MVP. Schema defined in `sql/001_create_messages.sql`; repository adapter and chat wiring pending |
| `create_task` tool (MCP) | ⏳ | Planned (day 3) |
| Evaluation (RAGAS) | ⏳ | Planned |
| Cost / latency logging | ⏳ | Planned; `max_tokens=1024` cap is already set |
| Frontend | 🟡 | Chat UI with streaming; document list, upload and status use real data. Citations and telemetry are hidden until the backend provides data |
| Automated tests | ⏳ | None yet |

## How it works

**Document upload (implemented)**

1. `POST /documents` validates the file type and rejects a duplicate filename.
2. The file is saved to Supabase Storage and a row is created in the `documents` table with status `processing`.
3. A background task extracts the text (`pypdf` in layout mode for PDFs), splits it into chunks of 2000 characters (about 500 tokens) with 200 characters of overlap, embeds each chunk with OpenAI `text-embedding-3-small` (1536 dimensions), and upserts the vectors to Pinecone with metadata (`text`, `document_id`, `chunk_index`, `document_filename`).
4. The status changes to `processed` (or `failed`, with the traceback logged) and the result is pushed to the client.

**Chat message (retrieval implemented; history, tool and citations pending)**

1. The user sends a question.
2. The backend embeds the question and runs a top-k similarity search in Pinecone, dropping matches below `min_score`. *(done)*
3. It builds the prompt: system instructions + retrieved chunks wrapped in `<reference_data>` (untrusted data, passed in the `system` parameter) + the question. Recent history is not included yet. *(done, except history)*
4. It calls the LLM with the `create_task` tool available. *(not started)*
5. The model answers with citations, or calls `create_task` to flag a follow-up when the documents can't answer. *(not started)*
6. The response streams back; tokens, latency and cost are logged. *(streaming done; metrics not started)*

## Architecture

The backend follows a hexagonal (ports and adapters) layout: the domain defines ports, the infrastructure implements them, and the application layer wires them together. Swapping a vendor (for example Pinecone for Qdrant) means writing a new adapter and leaving the services untouched.

```
app/
├── main.py                     # entrypoint, CORS, router registration
├── api/
│   ├── routers/                # chat.py, documents.py (HTTP only)
│   └── schemas/                # request/response models (Pydantic)
├── application/                # use cases: chat, retrieval, upload, process document
├── domain/
│   ├── chat/                   # Message entity, LLMClient port
│   ├── documents/              # Document entity; extractor, notifier, repository, storage ports
│   └── rag/                    # Chunk and RetrievedChunk entities; embedding and vector store ports; chunking
└── infrastructure/             # adapters
    ├── anthropic/              # LLM client (streaming)
    ├── openai/                 # embeddings
    ├── pinecone/               # vector store
    ├── supabase/               # document repository and file storage
    ├── extractors/             # PDF and text extractors
    └── memory/                 # in-memory SSE notifier
frontend/                       # React + TypeScript + Vite
sql/                            # database schema scripts, applied in order (see Setup)
docs/                           # design document
```

## Tech stack

| Layer | Tool | Status |
| --- | --- | --- |
| Backend | Python + FastAPI | ✅ |
| LLM | Anthropic Claude (Python SDK), `claude-haiku-5-5` for testing | ✅ |
| Embeddings | OpenAI `text-embedding-3-small` | ✅ |
| Vector database | Pinecone (serverless, cosine) | ✅ |
| Database + file storage | Supabase (Postgres + Storage) | ✅ |
| PDF extraction | `pypdf` | ✅ |
| Frontend | React, TypeScript, Vite | 🟡 |
| Orchestration | LangGraph | ⏳ Undecided: tool-calling loop or SDK directly |
| Tool standard | MCP | ⏳ `create_task` |
| Evaluation | RAGAS | ⏳ |
| Observability | LangSmith | ⏳ |
| Deployment | Vercel + Modal/Render | ⏳ |

## Setup

**Prerequisites:** Python 3, Node.js, and accounts for Anthropic, OpenAI, Supabase and Pinecone.

**1. External services**

- **Pinecone:** create a serverless index with 1536 dimensions and the cosine metric.
- **Supabase:** create a project, then:
  1. Create a Storage bucket named `AI_DOCUMENT_ASSISTANT`.
  2. Open the SQL Editor and run the scripts in `sql/` in order: `000_create_documents.sql`, then `001_create_messages.sql`. They create the tables and enable Row Level Security on them.

  The backend connects with the secret key, which bypasses Row Level Security. The tables have it enabled and no policies, so the public API cannot read or write them. The schema is applied by hand with these versioned scripts; there is no migration tool yet (see Known limitations).

**2. Backend**

```
git clone <repo-url>
cd ai-document-assistant

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root (never commit it):

```
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
SUPABASE_URL=
SUPABASE_SECRET_KEY=
PINECONE_API_KEY=
PINECONE_INDEX_NAME=
```

Run the server:

```
make dev
```

This runs `uvicorn app.main:app --reload` on `http://localhost:8000`.

**3. Frontend**

```
cd frontend
npm install
npm run dev
```

The dev server runs on `http://localhost:5173`, the origin allowed by the backend's CORS configuration.

## Testing the endpoints

Upload a document (returns 400 for unsupported types and 409 for a duplicate filename):

```
curl -F "file=@document.pdf;type=application/pdf" http://localhost:8000/documents
```

Watch its processing status, using the `id` from the previous response:

```
curl -N http://localhost:8000/documents/<id>/status
```

List uploaded documents:

```
curl http://localhost:8000/documents
```

Stream a chat response (`-N` disables curl's output buffering, so you see the chunks arrive):

```
curl -N -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Say hello in one sentence"}'
```

## Roadmap

- [x] FastAPI skeleton, streaming chat endpoint
- [x] Ports-and-adapters backend structure
- [x] Document upload, storage and ingestion pipeline (Pinecone)
- [x] Processing status streamed to the client
- [x] Retrieval wired into chat (`<reference_data>` injection)
- [x] Frontend wired to the real backend for documents (list, upload, status)
- [ ] Message history persisted and used in chat
- [ ] Visible citations in the UI
- [ ] `create_task` tool via MCP, with argument guard and tasks view
- [ ] Prompt-injection guardrail tested with a malicious document
- [ ] Golden eval set (15-20 Q&A pairs) and RAGAS scoring
- [ ] Cost/latency logging (LangSmith) and prompt caching
- [ ] Deployment, demo and final write-up

## Known limitations

- No auth and no per-user scoping: retrieval spans all uploaded documents. Acceptable for a single-user demo.
- Supabase's free tier pauses on inactivity (`GET /documents` then fails with a 500 and a name-resolution error); resume the project from the dashboard.
- The database schema is applied by hand from the scripts in `sql/`; there is no migration tool (such as Alembic) yet.
- `documents.filename` has no unique constraint: the duplicate check lives only in application code (`exists_by_filename`), so two simultaneous uploads of the same name could both pass.
- CORS only allows `http://localhost:5173` and the frontend API URLs are hard-coded to `127.0.0.1:8000`, so it is not deployable as is.

## Safety notes

- Retrieved content is wrapped in explicit `<reference_data>` markers, with a system-prompt instruction to treat it as data and never as instructions. This is a soft (learned) defense, not an architectural guarantee, and it has not yet been tested with a malicious document.
- The planned `create_task` tool is create-only, with no update, delete or external side effects. That is a hard, architectural limit on the worst case if the soft defense fails.
- Error details from unexpected failures are logged on the server and never returned to the client.