# AI Document Assistant

A full-stack document Q&A assistant: upload documents, ask questions, get grounded answers with citations. Built as a portfolio project to demonstrate AI engineering skills at the application layer (RAG, agentic tool use, eval design, cost/observability) on top of an existing full-stack background.

## Status

Document ingestion is complete end to end. Retrieval (grounding chat answers in the uploaded documents) is the next block; until then, `POST /chat` answers from the model alone.

| Area | Status | Notes |
| --- | --- | --- |
| `GET /health` | ✅ | Liveness check |
| `POST /documents` | ✅ | Validates type (PDF/text), rejects duplicate filenames (409), stores the file, and starts background processing |
| `GET /documents/{id}/status` | ✅ | Server-Sent Events stream: `processed` or `failed` |
| `POST /chat` | 🟡 | Streams a Claude response over SSE. Single-turn, no history, no retrieval yet |
| Ingestion pipeline | ✅ | Extract → chunk → embed → upsert to Pinecone → update status |
| Retrieval + citations | ⏳ | Next |
| `create_task` tool (MCP) | ⏳ | Planned |
| Evaluation (RAGAS) | ⏳ | Planned |
| Cost / latency logging | ⏳ | Planned |
| Frontend | 🟡 | Chat UI with a streaming client; the sources/citations panel still uses mock data and there is no upload UI yet |

## How it works

**Document upload (implemented)**

1. `POST /documents` validates the file type and rejects a duplicate filename.
2. The file is saved to Supabase Storage and a row is created in the `documents` table with status `processing`.
3. A background task extracts the text (`pypdf` in layout mode for PDFs), splits it into chunks of 2000 characters (about 500 tokens) with 200 characters of overlap, embeds each chunk with OpenAI `text-embedding-3-small` (1536 dimensions), and upserts the vectors to Pinecone with metadata (`text`, `document_id`, `chunk_index`).
4. The status changes to `processed` (or `failed`, with the traceback logged) and the result is pushed to the client over SSE.

**Chat message (target design; retrieval not implemented yet)**

1. The user sends a question.
2. The backend embeds the question and runs a top-k similarity search in Pinecone.
3. It builds a prompt: system instructions + retrieved chunks wrapped in `<reference_data>` (untrusted data) + recent history + the question.
4. It calls the LLM with the `create_task` tool available.
5. The model answers with citations, or calls `create_task` to flag a follow-up when the documents can't answer.
6. The response streams back; tokens, latency and cost are logged.

## Architecture

The backend follows a hexagonal (ports and adapters) layout: the domain defines ports, the infrastructure implements them, and the application layer wires them together. Swapping a vendor (for example Pinecone for Qdrant) means writing a new adapter and leaving the services untouched.

```
app/
├── main.py                     # entrypoint, CORS, router registration
├── api/
│   ├── routers/                # chat.py, documents.py (HTTP only)
│   └── schemas/                # request/response models (Pydantic)
├── application/                # use cases: chat, upload, process document
├── domain/
│   ├── chat/                   # Message entity, LLMClient port
│   ├── documents/              # Document entity; extractor, notifier, repository, storage ports
│   └── rag/                    # Chunk entity; embedding and vector store ports; chunking
└── infrastructure/             # adapters
    ├── anthropic/              # LLM client (streaming)
    ├── openai/                 # embeddings
    ├── pinecone/               # vector store
    ├── supabase/               # document repository and file storage
    ├── extractors/             # PDF and text extractors
    └── memory/                 # in-memory SSE notifier
frontend/                       # React + TypeScript + Vite
```

## Tech stack

| Layer | Tool | Status |
| --- | --- | --- |
| Backend | Python + FastAPI | ✅ |
| LLM | Anthropic Claude (Python SDK) | ✅ |
| Embeddings | OpenAI `text-embedding-3-small` | ✅ |
| Vector database | Pinecone (serverless, cosine) | ✅ |
| Database + file storage | Supabase (Postgres + Storage) | ✅ |
| PDF extraction | `pypdf` | ✅ |
| Frontend | React, TypeScript, Vite | 🟡 |
| Orchestration | LangGraph | ⏳ Tool-calling loop |
| Tool standard | MCP | ⏳ `create_task` |
| Evaluation | RAGAS | ⏳ |
| Observability | LangSmith | ⏳ |
| Deployment | Vercel + Modal/Render | ⏳ |

## Setup

**Prerequisites:** Python 3, Node.js, and accounts for Anthropic, OpenAI, Supabase and Pinecone.

**1. External services**

- **Pinecone:** create a serverless index with 1536 dimensions and the cosine metric.
- **Supabase:** create a Storage bucket named `AI_DOCUMENT_ASSISTANT` and a `documents` table with the columns `id`, `filename`, `storage_path`, `status`, `created_at`.

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

Stream a chat response (`-N` disables curl's output buffering, so you see the chunks arrive):

```
curl -N -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Say hello in one sentence"}'
```

## Roadmap

- [x] FastAPI skeleton, streaming chat endpoint (SSE)
- [x] Ports-and-adapters backend structure
- [x] Document upload, storage and ingestion pipeline (Pinecone)
- [x] Processing status over SSE
- [ ] Retrieval wired into chat, with citations
- [ ] Frontend wired to the real backend (upload, sources)
- [ ] `create_task` tool via MCP, prompt-injection guardrails
- [ ] Golden eval set (15-20 Q&A pairs) and RAGAS scoring
- [ ] Cost/latency logging (LangSmith) and prompt caching
- [ ] Deployment, demo and final write-up

## Safety notes

- Retrieved content will be wrapped in explicit `<reference_data>` markers, with a system-prompt instruction to treat it as data and never as instructions. This is a soft (learned) defense, not an architectural guarantee.
- The planned `create_task` tool is create-only, with no update, delete or external side effects. That is a hard, architectural limit on the worst case if the soft defense fails.
- Error details from unexpected failures are logged on the server and never returned to the client.