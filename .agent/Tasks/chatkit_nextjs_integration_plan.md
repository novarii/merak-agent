# ChatKit Integration Plan — Python Server ↔ Next.js Frontend

## Objective
- Expose the existing Merak Trip Planner agent through a ChatKit-compliant FastAPI endpoint and surface it via the forthcoming Next.js UI.
- Ensure realtime streaming (SSE), attachment handling hooks, and client tool support align with the [ChatKit server guidance](System/chatkit-docs.md) and Next.js streaming capabilities.

## References
- `.agent/System/chatkit-docs.md` — primary server/API contract.
- `.agent/System/project_architecture.md` — current Python runtime layout.
- `.agent/Tasks/frontend_next_plan.md` — broader frontend roadmap that this plan complements.
- Next.js Route Handlers streaming docs (`Response` + `ReadableStream`) for proxying SSE.
- ChatKit JS client docs for client tool callbacks and theming.

## Assumptions & Constraints
- Python runtime stays on 3.11 with Agents SDK already installed; add `openai-chatkit` via `pip install`.
- Initial data persistence leverages `chatkit.stores.SQLiteStore` for rapid prototyping; production path will migrate to Postgres per architecture goals.
- Attachments are optional in MVP but we scaffold interfaces so future blob storage can plug in.
- Next.js app targets React 19 / Node 24.5+ and will proxy to Python service running on `http://localhost:8000/chatkit` in dev.
- No end-user auth in v0; backend uses server-held API key. Thread/user IDs default to anonymous until we integrate identity.

## Workstreams

### 1. Python ChatKit Server Foundations
- Add `openai-chatkit` to `requirements.txt` and regenerate lock if necessary.
- Implement `MerakChatKitServer` in `src/merak_agent/workflows/chatkit_server.py`:
  - Subclass `ChatKitServer`.
  - Reuse `TripPlanner` agent; wire `Runner.run_streamed` with `stream_agent_response`.
  - Populate `AgentContext` with FastAPI request metadata (user id, feature flag).
  - Gate optional `client_tool_call` behavior (none in MVP, but leave hook).
- Provide dev-grade persistence:
  - Instantiate `SQLiteStore` (file-backed path for repeatable threads).
  - Stub `AttachmentStore` with `NotImplementedError` for upload operations, but include structure per docs.
- Create FastAPI router (`/chatkit`) returning SSE when `StreamingResult`, JSON otherwise.
  - Use request body passthrough to `server.process`.
  - Propagate `X-User-ID` header into context for future access control.
- Add entry script in `scripts/run_chatkit_server.py` with uvicorn launcher and environment flag `MERAK_ENABLE_CHATKIT_SERVER`.
- Document setup in `README.md` and `.env.example` (e.g., `CHATKIT_SERVER_PORT`).

### 2. Next.js Backend Proxy (API Route)
- Within `frontend/merak_web`, add route handler `app/api/chatkit/route.ts` (App Router):
  - Accept POST payload matching ChatKit client.
  - Forward to Python `/chatkit` with `fetch` using `stream: true`.
  - Mirror SSE headers (`text/event-stream`, `Cache-Control: no-store`).
  - Handle non-streaming JSON responses gracefully.
  - Inject server-side API key (from env) rather than exposing to browser.
- Add retry/backoff on network errors and surface HTTP errors as JSON for the client.

### 3. ChatKit Client Wiring (Next.js UI)
- Install `@openai/chatkit` (or `@openai/chatkit-react` if we opt for React hook).
- Create `useChatKitClient` hook to:
  - Initialize ChatKit with server-provided `clientToken` (stubbed by backend route for now).
  - Manage thread persistence (localStorage) and SSE subscription to `/api/chatkit`.
  - Handle `onClientTool` callback even if we only log unsupported tools in MVP.
- Build chat page component rendering `<ChatKit control={control} />`, align styles with design tokens.
- Support widget rendering per docs (Markdown/Text) and log unsupported widget types for telemetry.

### 4. Token & Secret Flow
- Implement Next.js API routes `/api/chatkit/start` and `/api/chatkit/refresh`:
  - Call Python backend endpoints (to be added) that generate client secrets via ChatKit server.
  - Cache client secret server-side with expiry tracking; align with ChatKit docs for rotation.
- Update Python server to expose lightweight endpoints (or extend `/chatkit`) for token issuance using `server.create_client_secret`.

### 5. Attachments & Client Tools (Scaffold)
- Define placeholder `AttachmentStore` class that raises `NotImplementedError` but enumerates required methods.
- Expose TODOs for:
  - Two-phase upload (registration endpoint returning signed URL).
  - Direct upload handling via FastAPI.
- In Next.js, prepare client composer extension points for file attachments and tools (`setOptions({ composer: { tools: [...] }})`), but keep disabled until backend ready.

### 6. Observability & Docs
- Add structured logging (request id, thread id) in FastAPI endpoint.
- Update `.env.example`, root `README.md`, and `.agent/System` docs describing new services and local dev workflow.

## Milestones & Deliverables
1. **Backend MVP** — FastAPI server running locally, streaming responses from agent.
2. **Proxy & UI Skeleton** — Next.js API route relaying to backend; basic chat UI renders streamed text.
3. **Token Flow & Context Hooks** — Secure client secret issuance and context propagation.
4. **Extended Features** — Attachment scaffolding, client tools, widget coverage.
5. **Docs & Ops** — Updated documentation/checklists for contributors and operational logging hooks.

## Risks & Mitigations
- **Streaming mismatch between FastAPI and Next.js** — Validate SSE passthrough manually and align headers to avoid buffering; consider `asyncio.to_thread` if necessary.
- **Token leakage** — Keep secrets server-side; use Next.js Route Handler (server component) and secure env handling.
- **Attachment backlog** — Track as follow-up issues; ensure clear TODOs so contributors know limitations.
- **Agent regression under SSE** — Monitor logging output and provide a JSON fallback path when streaming fails.
