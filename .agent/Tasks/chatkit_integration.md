# Trip Planner ChatKit Integration Plan

## Goal
Expose the existing Trip Planner agent through an OpenAI ChatKit compatible backend so the web ChatKit client can drive multi-turn itineraries with streaming responses, attachments (future), and thread persistence.

## References
- **ChatKit Python Server Docs:** `https://openai.github.io/chatkit-python/server` – lifecycle, FastAPI wiring, and streaming patterns.
- **Agent Input Conversion:** `https://openai.github.io/chatkit-python/api/chatkit/agents` – `simple_to_agent_input`, `ThreadItemConverter`, and tool-call handling.
- **Storage Contracts:** `https://openai.github.io/chatkit-python/api/chatkit/store` – required `Store` CRUD methods for threads, items, and attachments.

## Deliverables
1. Python package updates with ChatKit/FastAPI dependencies and configuration surface.
2. ChatKit-aware server module that wraps the Trip Planner agent and streams results.
3. HTTP entry point for local demos (`/chatkit`), including SSE and JSON fallbacks.
4. Backing store implementation aligned with our SQLite session model (with room for Postgres migration).
5. Automated tests covering the ChatKit server adaptor and FastAPI route.
6. Updated docs (README + `.agents/System`) describing setup, configuration, and future enhancements.

## File-Level Plan

### Dependency & Configuration
- **pyproject.toml**, **requirements.txt**
  - Add `openai-chatkit`, `fastapi`, `uvicorn[standard]`, and any serialization helpers noted in the ChatKit docs.
  - Introduce optional extras or `CHATKIT_MODEL` env config for selecting the OpenAI model (`gpt-4.1` per docs).
- **.env.example** *(if present)* / create if missing
  - Document new env variables (`OPENAI_API_KEY`, `CHATKIT_MODEL`, `CHATKIT_DB_URL`).

### ChatKit Storage Layer
- **src/merak_agent/workflows/chatkit_store.py** *(new)*
  - Implement a lightweight `ChatKitSQLiteStore` subclassing `chatkit.store.Store`, persisting threads/items in SQLite.
  - Align schema with existing `SQLiteSession` expectations; add TODO for Postgres migration referencing docs’ recommendation for durable stores.
- **tests/workflows/test_chatkit_store.py** *(new)*
  - Unit tests mocking SQLite connection to verify `load_thread`, `add_thread_item`, and pagination behavior.

### ChatKit Server Wrapper
- **src/merak_agent/workflows/chatkit_server.py** *(new)*
  - Subclass `ChatKitServer`.
  - Instantiate `create_trip_planner_agent()` once.
  - In `respond`, follow `Runner.run_streamed` + `stream_agent_response` pattern from the server docs; leverage `simple_to_agent_input`.
  - Support optional attachment store plumbing (stubbed for now with `NotImplementedError`).
- **tests/workflows/test_chatkit_server.py** *(new)*
  - Stub the store and `Runner.run_streamed` to assert streaming events are forwarded and errors handled.

### FastAPI Surface
- **scripts/run_chatkit_server.py** *(new)*
  - CLI to bootstrap FastAPI app and expose `/chatkit` POST, `/healthz` GET.
  - Use documented FastAPI example: return `StreamingResponse` when `StreamingResult` is emitted, else JSON.
  - Wire configurable host/port via argparse.
- **tests/integration/test_chatkit_endpoint.py** *(new)*
  - Use `httpx.AsyncClient` or FastAPI’s test client to simulate user posts, ensuring status codes and stream content.

### Shared Utilities & Config
- **src/merak_agent/common/config.py** *(new or existing)*
  - Centralize configuration loading for model name, database URL, etc., so both CLI and server stay in sync.
- **scripts/run_trip_planner.py**
  - Optionally add helper flag or cross-reference to ChatKit server for discoverability.

### Documentation
- **README.md**
  - Add “ChatKit Server” section with setup commands (`pip install`, `python3 scripts/run_chatkit_server.py`, frontend expectations).
  - Mention SSE streaming and `--single-turn` CLI fallback.
- **.agents/System/project_architecture.md**
  - Extend architecture overview with ChatKit flow diagram narrative (HTTP -> FastAPI -> ChatKitServer -> Runner).
- **.agents/Tasks/trip_planner.md**
  - Reference this integration plan and note new development milestones.
- **docs/** *(if a docs folder exists)*
  - Optional quickstart or API reference for ChatKit consumers.

### Testing & QA
- Update **Makefile** (when available) or provide `make chatkit-server` target for developers.
- Ensure `pytest` includes new modules; update coverage expectations.
- Consider adding smoke test script that posts a canned request against local server.

### Follow-Up Enhancements (Document Only)
- Attachments: evaluate `AttachmentStore` integration per docs once requirements solidify.
- Client tool calls: leverage `ClientToolCall` integration to trigger frontend widgets.
- Deployment: capture Kubernetes/Container guidance if server graduates from demo to production.

