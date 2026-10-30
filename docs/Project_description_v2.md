# Design document: AI document assistant

**Author:** Lorena
**Status:** In progress (updated 2026-10-27). Ingestion and retrieval done, agent tool call next
**Timeline:** 7-day plan (days 1-2 done; day 3 in progress)
**Repo:** https://github.com/LorenaGRB/ai-document-assistant
**Purpose:** Demonstrate AI engineering competency (RAG, agent orchestration, eval design, cost/observability) on top of existing fullstack skills

> This version replaces the original design document. Sections 1-11 keep the original design (with corrections where the real implementation differs). Sections 12-16 are new: decisions made, audit of the real state, remaining work, and known issues. The state described here comes from a code audit plus the working sessions. Anything that could not be verified is marked **unverified**.

---

## 0. Status at a glance

**Done**
- Ingestion pipeline end to end: upload, extract, chunk, embed, Pinecone upsert, status streaming.
- Retrieval wired into chat with `<reference_data>` injection and an anti-prompt-injection instruction.
- Frontend connected to real data for documents (list, upload, status). No mock data in use.
- Hexagonal architecture (ports and adapters) in place and respected.

**In progress / next**
- Persisting chat history (`messages` table). Required for the MVP: the chat has no memory between turns today.
- `create_task` as an MCP tool (day 3).

**Not started**
- Visible citations (backend never sends them), `create_task` / MCP, tasks table and view, evaluation (golden set, RAGAS), LangSmith, cost/latency logging, prompt caching, deployment, automated tests.

---

## 1. Overview

A web application where a user uploads documents, asks questions about them in a chat interface, and receives grounded answers with citations back to source text. When the assistant cannot fully answer from the documents, it can take one bounded action, creating a follow-up task, rather than guessing.

This is not a chatbot wrapper. It is a small but complete AI product feature: retrieval, agentic tool use, evaluation, and cost tracking, wired into a normal fullstack app and deployed publicly.

**Domain:** pick something you can speak to with real specifics. The architecture is domain-agnostic. Currently tested with two real PDFs (a Q&A system for learning Python, and a STAR interview prep guide).

---

## 2. Goals and non-goals

**Goals**
- Ship a deployed, working AI feature end to end, not a local script
- Demonstrate retrieval-augmented generation with visible citations
- Demonstrate one well-scoped agentic tool call, not a general-purpose agent
- Produce a golden evaluation set and a repeatable scoring process
- Track token cost and latency per request
- Apply at least one concrete safety guardrail (prompt-injection resistance via untrusted-content handling)

**Non-goals**
- No model fine-tuning or training
- No multi-agent orchestration (one tool is enough to prove the pattern)
- No custom infrastructure: managed services only (hosted Postgres, serverless deploy)
- No auth/multi-tenancy complexity: single-user or simple session-based access is fine

---

## 3. System architecture

```
┌─────────────┐        ┌──────────────────┐        ┌────────────────┐
│   Frontend   │  HTTP  │  Backend (FastAPI)│  API   │   LLM provider  │
│  Chat + Upload│ ─────▶│  RAG + Agent logic│ ─────▶ │ (Claude/OpenAI) │
└─────────────┘        └────────┬─────────┘        └────────────────┘
                                 │
                    ┌────────────┼─────────────┐
                    ▼            ▼             ▼
             ┌───────────┐ ┌───────────┐ ┌────────────┐
             │Vector DB   │ │ Relational│ │ Eval/cost   │
             │(Pinecone)  │ │ DB (tasks,│ │ logs        │
             │            │ │ messages) │ │ (LangSmith) │
             └───────────┘ └───────────┘ └────────────┘
```

**Request lifecycle (chat message), target design**
1. User sends a question in the chat UI.
2. Backend embeds the question and runs a similarity search against the vector store (top-k, filtered by minimum score). *(done)*
3. Backend builds the prompt: system instructions + retrieved chunks marked as untrusted reference data + recent conversation history + the question. *(done, except conversation history)*
4. Backend calls the LLM with the `create_task` tool defined and available. *(not started)*
5. If the model has enough grounded context, it answers directly with citations. If not, it may request `create_task` to flag a follow-up. The backend validates the arguments with a guard before executing anything. *(not started)*
6. Response streams back to the frontend; citations render inline; token count, latency, and cost are logged. *(streaming done; citations, metrics not started)*

**Request lifecycle (document upload), implemented**
1. `POST /documents` validates the type (PDF or UTF-8 text) and rejects a duplicate filename with 409.
2. The file goes to Supabase Storage and a `documents` row is created with status `processing`.
3. A background task extracts the text, chunks it (2000 chars, 200 overlap, ~500 tokens), embeds each chunk, and upserts vectors to Pinecone with metadata (`text`, `document_id`, `chunk_index`, `document_filename`).
4. Status becomes `processed` or `failed` (traceback logged) and is pushed to the client through an in-memory notifier, streamed from `GET /documents/{id}/status`.

---

## 4. Tech stack

| Layer | Tool | Rationale | Status |
|---|---|---|---|
| Frontend | React + TypeScript + Vite | Existing skill; streaming rendering is the only new piece | Partially done |
| Backend | Python + FastAPI | Pairs natively with the Python AI ecosystem | Done |
| LLM API | Anthropic Claude API (direct SDK), OpenAI as secondary reference | Direct SDK calls for the core loop so each step can be explained | Done (`claude-haiku-5-5` for testing) |
| Embeddings | OpenAI `text-embedding-3-small` (1536 dim) | Cheap, standard | Done |
| Vector database | Pinecone (serverless, cosine, AWS us-east-1) | Named in job postings; free tier is enough | Done |
| Database + file storage | Supabase (Postgres + Storage) | Managed, no infra to own | Done (`documents` only) |
| PDF extraction | `pypdf` | Simple, no extra services | Done |
| Orchestration | LangGraph | Highest-signal orchestration framework in postings | **Undecided**: use it for the tool-calling loop or the SDK directly? |
| Tool-calling standard | MCP | `create_task` as an MCP server, backend as MCP client | Not started |
| Evaluation | RAGAS | Faithfulness and answer relevancy | Not started |
| Observability | LangSmith | Near-zero-code tracing; tokens, latency, cost | Not started |
| Deployment | Vercel (frontend) + Modal or Render (backend) | Managed | Not started |

---

## 5. Component design

### 5.1 Frontend
- Chat interface with streaming token rendering *(done)*
- Document upload with processing-status indicator *(done)*
- Citations rendered as clickable references to source chunks *(UI shell exists: `Citation` type, `CitationPanel`, `Message` support; backend sends no citation data yet)*
- A small running cost/latency indicator per response, a deliberate product decision that signals cost-awareness *(`Telemetry.tsx` is hidden until real data exists)*
- Tasks view to list tasks the agent created *(not started)*

### 5.2 Backend / API layer
- `POST /documents`: upload and ingest a document *(done)*
- `GET /documents`: list documents, newest first *(done)*
- `GET /documents/{id}/status`: stream processing status *(done)*
- `POST /chat`: send a message, returns a streamed response with citations and tool-call metadata *(streaming + retrieval done; single-turn, no history, no `conversation_id`)*
- `GET /tasks`: list tasks the agent created *(not started)*
- `POST /eval/run`: trigger the evaluation harness *(not started)*
- `GET /health` *(done)*

### 5.3 RAG pipeline
- Chunking: fixed-size, 2000 chars with 200 overlap (~500 tokens, 10% overlap). Document if switching to semantic chunking and why.
- Embeddings via OpenAI `text-embedding-3-small`.
- Retrieval: cosine similarity, `top_k=5`, filtered by `min_score=0.3` (this threshold has not been validated against real cases yet). Hybrid search is a stretch goal.
- Retrieved chunks are wrapped in the prompt as `<reference_data>`, passed in the `system` parameter (the Anthropic messages list only accepts `user`/`assistant` roles). The system prompt instructs the model to treat their contents as data, never as instructions.
- Chunks are formatted as `[document_filename, chunk index N] text` so citations are readable.

### 5.4 Agent & tool calling
- A **tool call** is the structured request the model returns when it decides to use a tool: tool name plus proposed arguments. The model never executes anything. The backend reads the request, validates it with a guard, and decides whether to run the real function.
- Single tool: `create_task(title, description, source_message_id)`. `source_message_id` is injected by the backend, not invented by the model, and requires message persistence.
- Scope: create-only, no update/delete, no external side effects (no email sending, no irreversible actions).
- Exposed as an **MCP server** (a separate process that describes the tool in a standard format and executes it). The backend acts as the MCP client. MCP is to agents what HTTP is to API communication: a standard protocol, not a library.
- The "agent" is the whole system (the backend + the LLM as decision-making brain + the code that executes the action), not the LLM alone. The chatbot becomes an agent at the moment the model can request an action instead of only returning text.
- The model is instructed to use the tool only when it cannot answer confidently from retrieved context. This is the one decision point worth documenting carefully ("when NOT to use an agent" is a common interview question).
- Edge case to define: when the `min_score` filter leaves no chunks, `reference_data` is empty. That is exactly the case that should trigger `create_task`.
- `stream_reply` currently yields text only. Tool-use blocks inside the stream need separate handling.

### 5.5 Evaluation harness
- A golden set of 15-20 question/answer pairs against the real documents, covering:
  - Directly answerable questions (retrieval should succeed)
  - Questions requiring synthesis across multiple chunks
  - Out-of-scope questions (correct behavior is to say so, or trigger `create_task`, not hallucinate)
- Scoring via RAGAS faithfulness and answer relevancy, plus a manual pass/fail column for out-of-scope cases
- Output: `eval_results.md` with per-question scores and a summary metric, plus at least one documented retrieval fix driven by a failure
- Use this phase to calibrate `min_score` and `top_k`

### 5.6 Observability & cost tracking
- Every LLM call logged via LangSmith: input/output tokens, latency, estimated cost
- Metrics stored in the `messages` table
- A simple aggregate view: total cost, average cost per query, average latency
- Prompt caching on the system prompt and retrieved context block, with the measured cache hit rate and cost savings

---

## 6. Data model

```
documents(id, filename, uploaded_at)                                  -- exists (with status)
chunks(id, document_id, content, embedding, chunk_index)              -- lives in Pinecone, not Postgres
conversations(id, created_at)                                         -- to decide: how conversations are created
messages(id, conversation_id, role, content, citations, tokens_in, tokens_out, cost_usd, latency_ms, created_at)  -- not started
tasks(id, title, description, source_message_id, created_at)          -- not started
eval_runs(id, question, expected_answer, actual_answer, faithfulness_score, relevancy_score, passed, run_at)     -- not started
```

The `messages` table is shared by three pending features: conversational memory, visible citations, and cost/latency tracking.

---

## 7. Safety & guardrails

| Risk | Mitigation | Status |
|---|---|---|
| Prompt injection via uploaded documents | Retrieved content framed as data in the system prompt; model told to ignore instructions inside it | Implemented, **not yet tested** with a malicious document |
| Excessive agency | The one tool is create-only; arguments validated by a guard before execution; the model never executes directly | Planned |
| Hallucinated answers presented as fact | Citations mandatory in the UI; eval set tests out-of-scope questions | Planned |
| Runaway cost | Cost logging per request; hard `max_tokens` cap | Cap set (`max_tokens=1024`, hard-coded in `AnthropicLLMClient`); logging not started |
| Error leakage | Error details logged server-side, not returned to the client | Implemented for document processing |
| No auth, no per-user scoping | Retrieval is not scoped per user or per document. Acceptable for a single-user portfolio demo; note it in the final README | Open |

---

## 8. Implementation timeline

| Days | Milestone | Status |
|---|---|---|
| 1-2 | Core fullstack app, ingestion, retrieval wired into chat | Done (citations not wired) |
| 3 | Agent tool call (`create_task`) via MCP, guardrails, prompt-injection handling | In progress (concepts covered, message persistence first) |
| 4 | Golden eval set + RAGAS scoring; iterate on chunking/retrieval | Not started |
| 5 | Cost/latency logging via LangSmith; prompt caching; cost dashboard | Not started |
| 6-7 | Polish, error handling, deploy, README, demo | Not started |

---

## 9. Definition of done

- [x] FastAPI skeleton, streaming chat endpoint
- [x] Ports-and-adapters backend structure
- [x] Document upload, storage and ingestion pipeline (Pinecone)
- [x] Processing status streamed to the client
- [x] Retrieval wired into chat (`<reference_data>` injection)
- [x] Frontend wired to the real backend for documents (list, upload, status)
- [ ] Message history persisted and used in chat
- [ ] Visible citations in the UI
- [ ] `create_task` via MCP, with argument guard and tasks view
- [ ] Prompt-injection guardrail tested with a malicious document
- [ ] Golden eval set (15-20 pairs) run with RAGAS, results documented, at least one retrieval fix made in response to a failure
- [ ] Cost per query logged and reported (LangSmith) and prompt caching with measured hit rate
- [ ] Deployed and publicly reachable
- [ ] README with architecture, eval results, cost model, and at least one failure mode found and fixed
- [ ] Recorded demo

---

## 10. What this project demonstrates

| Interview topic | Where it's proven |
|---|---|
| RAG design | Chunking, embedding, retrieval with score filtering, citation rendering |
| Agent orchestration | Single-tool loop, explicit scoping, "when not to use an agent" reasoning, MCP client/server split |
| Eval design | Golden set, RAGAS metrics, a documented fix driven by eval results |
| Safety / guardrails | Prompt-injection handling, least-privilege tool design, argument validation before execution |
| Cost optimization | Per-request cost logging, prompt caching, measured savings |
| Observability | LangSmith tracing |
| Architecture | Hexagonal design: swapping a vendor means writing a new adapter |

---

## 11. Stretch goals (if time remains)

- Hybrid search (BM25 + vector) instead of pure vector retrieval
- A second tool with a confirmation step, to demonstrate human-in-the-loop design
- A basic model router (cheap model for simple queries, stronger model for synthesis)
- Regression testing: re-run the eval set automatically on any prompt or retrieval change

---

## 12. Decisions made

- **Hexagonal architecture** (domain / application / infrastructure / api). Ports live in the domain, adapters in infrastructure.
- **Direct Anthropic SDK** for the core loop. `claude-haiku-5-5` is used for testing because of a low credit balance; the final demo model is still to decide (it is a constructor default in `AnthropicLLMClient`).
- **Chunking:** 2000 chars / 200 overlap (changed from an initial 500/50 to reach ~500 tokens).
- **Document status via streaming, not polling.** The backend streams the status through an in-memory notifier; the frontend reads it with `fetch` and a stream reader, not `EventSource`.
- **Page numbers in citations dropped for now.** `pypdf` output is concatenated into one string, so page boundaries are lost. `document_filename` + `chunk_index` is enough.
- **Pinecone index recreated** (1536 dim, cosine, serverless AWS us-east-1) after the metadata schema changed, instead of patching old records with `.get()`.
- **`rag_content` goes in the `system` parameter**, not as a message in the list, because the Anthropic messages API only accepts `user`/`assistant` roles there.
- **Message history persistence is required for the MVP.** `send_message` currently builds a single-message list on every call, so there is no memory between turns. `source_message_id` for `create_task` comes almost free once messages are persisted. A retention policy (e.g. delete old conversations without tasks after ~1 month) is an optional future optimization.
- **Tool calls:** the model proposes, the backend validates and executes. The guard sits between the proposal and the real function.
- **GitHub Actions cron** (trigger `schedule`) will ping a lightweight Supabase REST endpoint to keep the free-tier project from pausing, instead of running an always-on server.

---

## 13. Audit: real state vs. design

| Item | State | Notes |
|---|---|---|
| `GET /health` | Done | |
| `POST /documents` | Done | Type validation, 409 on duplicate, storage + row, background task |
| `GET /documents` | Done | Newest first |
| `GET /documents/{id}/status` | Changed | Streams the bare status string with an event-stream content type but **no SSE framing**; read with `fetch`, not `EventSource` |
| `POST /chat` | Partially done | Streaming + retrieval; no history, no `conversation_id` |
| Retrieval | Done | `RetrievalService`, `PineconeVectorStore.search` |
| Citations (backend) | Not started | `RetrievedChunk` stays inside `ChatService`, never reaches the client |
| Citations (frontend UI) | Partially done | UI shell exists, fed by nothing. The SOURCES panel in the sidebar appears to list uploaded documents, not the sources of each answer (**unverified**) |
| `create_task` / MCP | Not started | No tool definitions, no MCP code |
| Message persistence | Not started | Only the in-memory `Message` dataclass exists |
| Evaluation | Not started | |
| Cost / latency logging | Not started | `Telemetry.tsx` is a stub returning `null` |
| Prompt caching, LangSmith, LangGraph | Not started | |
| Deployment | Not started | CORS allows only `http://localhost:5173`; API URLs hard-coded to `127.0.0.1:8000` |
| Tests | Not started | No test files in the repo. The "two PDFs, no cross-contamination" check was manual |

---

## 14. Remaining work

**Immediate (before continuing with `create_task`)**
- [ ] Persist chat history: `messages` table, `MessageRepository` (port + adapter), save each turn, pass history to Claude and to `/chat`
- [ ] Decide how conversations are created and how the frontend sends `conversation_id`

**Day 3: agent tool call**
- [ ] Define `create_task(title, description, source_message_id)`, create-only, as an MCP server with the backend as MCP client
- [ ] Argument guard that validates the model's proposal before executing
- [ ] Prompt instruction: call it only when it cannot answer confidently from `reference_data`
- [ ] Handle `tool_use` blocks inside the streaming response
- [ ] Define what the model sees when `min_score` filtering leaves `reference_data` empty (today the system prompt sends an empty `<reference_data></reference_data>` plus the "ONLY the data below" instruction)
- [ ] `tasks` table + `TaskRepository` (same pattern as `DocumentRepository`), `GET /tasks`, simple tasks view in the frontend
- [ ] Test the prompt-injection guardrail with a malicious uploaded document
- [ ] Confirm the hard `max_tokens` cap still holds once tools are added
- [ ] Decide whether to use LangGraph for the tool-calling loop or the SDK directly
- [ ] Decide where the MCP server runs in production
- [ ] End-to-end test with an out-of-scope question

**Day 4: evaluation**
- [ ] Golden set (15-20 questions: direct, synthesis, out-of-scope)
- [ ] RAGAS faithfulness and answer relevancy; manual pass/fail for out-of-scope
- [ ] `eval_results.md` with at least one documented retrieval fix
- [ ] `eval_runs` table and `POST /eval/run`
- [ ] Calibrate `min_score` (0.3 has not been validated against real cases)

**Day 5: cost and observability**
- [ ] LangSmith tracing
- [ ] Tokens / cost / latency stored in `messages`
- [ ] Prompt caching with measured hit rate
- [ ] Aggregate cost endpoint
- [ ] Re-enable `Telemetry.tsx` with real data

**Days 6-7: wrap up**
- [ ] Visible inline citations (decide how `RetrievedChunk` travels backend -> frontend: separate SSE event or header)
- [ ] Error handling and polish
- [ ] Deploy (Vercel + Modal/Render): configurable API base URL and CORS origins first
- [ ] Final README (architecture, eval results, cost model, failure modes)
- [ ] Recorded demo

**Loose items**
- [ ] GitHub Actions cron workflow pinging Supabase so the free-tier project doesn't pause again
- [ ] `DELETE /documents` (low priority; must also delete the Storage object and Pinecone vectors)
- [ ] Message retention policy (not needed for the MVP)
- [ ] Stretch goals from section 11

**Found in the audit**
- [ ] Add automated tests (none exist)
- [ ] Add SSE framing to the status endpoint, or document the raw-text contract; clean up notifier queues (never removed; `subscribe` serves only one status)
- [ ] Handle errors in `streamChat` / `useChatStream` (no `response.ok` check, no try/catch; a failed request leaves an empty assistant bubble; message ids use `Date.now()` and could collide)
- [ ] Fix port/adapter mismatches: `DocumentStorage` upload signature differs between port and adapter; `DocumentRepository.save` and `UploadDocumentService.execute` are typed `-> dict` but return `Document`
- [ ] Remove dead `frontend/src/data/mockData.ts`
- [ ] Update `README.md` (still says retrieval is next and the frontend uses mock sources)
- [ ] Optional: batch embedding calls during ingestion (currently one call per chunk); guard against empty extracted text

---

## 15. Known issues and open questions

- **Supabase free tier pauses on inactivity.** The symptom is `GET /documents` returning 500 with `httpcore.ConnectError: [Errno -2] Name or service not known` (the hostname stops resolving). Fix: "Resume project" in the dashboard (resumable until 23 Nov 2027). The planned permanent fix is the GitHub Actions cron ping.
- **Pinecone inactivity:** free plans have historically archived inactive indexes after a period. Whether this applies to a serverless index like this one is **unverified**.
- **`min_score=0.3`** is a default that was never validated against real questions.
- **LangGraph vs. direct SDK** for the tool-calling loop is undecided.
- **Where the MCP server runs in production** is undecided.
- **Final demo model** is undecided (testing uses `claude-haiku-5-5`).
- **No auth and no per-user scoping**, acceptable for the demo; document it in the README.
