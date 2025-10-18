# Frontend Implementation Plan — Next.js + ChatKit

## Objective
- Deliver a browser-based chat client for the Merak Trip Planner, powered by a Next.js server and React UI.
- Reuse the existing Python Agents runtime while exposing it through the ChatKit server workflow described in the [ChatKit Python documentation](https://openai.github.io/chatkit-python/server).

## Constraints & Assumptions
- Python backend continues to host the agent logic (`TripPlanner`), now surfaced via a `ChatKitServer.process` endpoint (per docs: instantiate a `ChatKitServer`, wire `Runner.run_streamed`, and return either `StreamingResponse` or JSON).
- Backend service runs as a FastAPI app served by `uvicorn`, keeping deployment simple and aligning with ChatKit server examples.
- Frontend is built with the latest Next.js release compatible with React 19 and uses TypeScript for React components.
- Runtime targets Node.js v24.5 or newer with React 19.2; ensure dependency versions and tooling (Next.js, ESLint, testing) align with this stack.
- Streaming is handled with Server-Sent Events (SSE) from the Next.js server to the browser; the Next.js route proxies responses from the Python FastAPI endpoint.
- Widget and client-side actions follow ChatKit guidance (`chatKit.setOptions({ widgets: { onAction }})`), enabling client-handled actions when widgets declare `ActionConfig(handler="client")`.
- Auth: initial version uses API key stored server-side and forwarded through backend-to-backend calls; no end-user auth.

## High-Level Architecture
1. **Python service**: Wrap current agent inside a FastAPI endpoint (`/chatkit`) using `MyChatKitServer` as shown in the docs (instantiate `Runner.run_streamed`, stream via `stream_agent_response`) and serve it with `uvicorn`.
2. **Next.js application**: Hosts both the React UI and an API route (`/api/chat`) that forwards requests to the Python `/chatkit` endpoint, piping SSE events back to the browser.
3. **React client**: Uses a chat UI component (custom or `@openai/chatgpt` style) that subscribes to the SSE stream, renders markdown widgets, and handles client actions.

## Implementation Phases

### Phase 0 — Planning & Scaffolding
- Define Python FastAPI app packaging as a standalone `uvicorn` service alongside existing scripts.
- Decide repository layout: create `frontend/merak_web/` (Next.js app) to keep parity with Python `src/`.
- Capture environment variables: `NEXT_PUBLIC_API_BASE_URL`, `CHATKIT_SERVER_URL`, `OPENAI_API_KEY` retained server-side.

### Phase 1 — Backend Readiness
- Add FastAPI entrypoint (`scripts/run_chatkit_server.py`) that instantiates `MyChatKitServer` as per docs, exposes `/chatkit`, and bootstraps `uvicorn` for serving.
- Ensure `Runner.run_streamed` wiring returns `StreamingResult` for SSE compatibility.
- Implement context propagation: call `server.process(body, {"userId": request.headers.get("X-User-ID", "anonymous")})` so the server can enforce permissions (`load_attachment` guards per documentation).
- Gate behind feature flag to avoid interfering with CLI workflow.

### Phase 2 — Next.js Project Bootstrap
- Initialize Next.js (TypeScript, App Router, ESLint) via `npx create-next-app@latest merak_web --ts --eslint`, pinning React to `19.2.x` and verifying the template runs under Node 24.5 or newer.
- Configure project-level lint/format rules to mirror repo standards (Prettier, ESLint; integrate with `ruff` workflow separately) and add `.nvmrc` or Volta/`engines` entries recommending Node 24.5+ without hard pinning.
- Add `package.json` scripts aligning with repo commands (`dev`, `build`, `lint`, `test`).
- Document frontend setup in root `README.md` appendix.

### Phase 3 — Shared UI Foundations
- Define layout shell (`app/layout.tsx`) with responsive container and theming.
- Create shared components: `ChatLayout`, `MessageList`, `MessageBubble`, `Composer`.
- Support markdown rendering using `react-markdown` for ChatKit's Markdown widgets (docs state `Markdown` widget streams markdown text).
- Establish design tokens (CSS variables or Tailwind) for consistent styling.

### Phase 4 — ChatKit Client Integration
- Build a client-side hook `useChatKitClient` that manages:
  - Thread creation and persistence (store thread ID in local storage).
  - SSE subscription to `/api/chat`.
  - Appending incoming ChatKit events (messages, widgets).
- Implement `/api/chat` route handler:
  - Forward POST body to Python `/chatkit`.
  - Set `Accept: text/event-stream` and stream results to the browser, copying event headers.
- Handle non-streaming responses (fallback to JSON) in accordance with the server docs.

### Phase 5 — Widgets & Client Actions
- Parse incoming widget payloads; support at least `Markdown`, `ListView`, and `Text` per documented widgets.
- Build widget renderer map keyed by `widget.type`.
- Implement client-side action handling: when a widget action uses `handler="client"`, route through `widgets.onAction` per docs and call `chatKit.sendAction` (or equivalent API POST) back to the server.
- Support client tool calls: detect `client_tool_call` items and prompt the user; once handled, POST to server’s `threads.add_client_tool_output`.

### Phase 6 — State & Persistence
- Maintain chat history in React state with fallback persistence (`IndexedDB` or localStorage) keyed by thread ID.
- Implement optimistic updates for user messages before server acknowledgment.
- Provide clear error states for network failures (retry, reconnect).

### Phase 7 — Observability & Telemetry
- Instrument API route with minimal logging (request ID, thread ID).
- Add client-side analytics hooks (console logging initially) for message lifecycle.
- Surface server progress events (`ProgressUpdateEvent` streaming) as temporary system messages/spinners.

### Phase 8 — Testing & QA
- Unit tests for React components (Jest + React Testing Library).
- Integration tests for `/api/chat` route using mocked FastAPI responses.
- Manual QA script covering:
  - Streaming itinerary generation.
  - Widget rendering (Markdown, list).
  - Client action flow (button triggers).
- Align QA with repository guidelines (pytest still covers backend; new tests introduced via frontend test runner).

## Deliverables
- `frontend/merak_web/` Next.js app with production build scripts.
- FastAPI ChatKit server entrypoint and `uvicorn` runner script.
- Updated `.env.example` documenting new variables.
- Documentation updates: root `README.md` frontend section, `.agent/System` or SOP updates if necessary.

## Open Questions
- Authentication: will future releases require user login or per-user sessions?
- Hosting strategy: serve Next.js and FastAPI separately or via reverse proxy?
- UI library preference (custom vs. adopting OpenAI ChatKit UI snippets).

## Risks & Mitigations
- **Streaming instability**: implement exponential backoff and event replay on disconnect.
- **Widget coverage**: start with Markdown/ListView/Text, log unsupported widget types for iterative support.
- **Tool call synchronization**: rely on `_cleanup_pending_client_tool_call` pattern to avoid orphaned pending calls; add automated cleanup job if users drop.
