# Trip Planner ChatKit Integration Plan (Prototype Scope)

## Goal
Expose the Trip Planner agent through an OpenAI ChatKit compatible backend to confirm streaming responses with the ChatKit SDK.

## References
- https://openai.github.io/chatkit-python/server — FastAPI wiring, streaming patterns, built-in `MemoryStore`.
- https://openai.github.io/chatkit-python/api/chatkit/agents — `simple_to_agent_input`, `stream_agent_response`, tool-call handling.

## Deliverables
1. Add minimal dependencies (`openai-chatkit`, `fastapi`, `uvicorn[standard]`) while reusing the existing `OPENAI_API_KEY`.
2. Create a lightweight ChatKit server shim that reuses `create_trip_planner_agent()` with the built-in `MemoryStore` and forwards streamed responses.
3. Provide a runnable script (e.g., `python3 scripts/run_chatkit_prototype.py`) exposing a `/chatkit` POST endpoint plus console instructions for manual validation.

## File-Level Plan

### Dependencies
- `pyproject.toml`, `requirements.txt`
  - Add `openai-chatkit`, `fastapi`, `uvicorn[standard]`; keep the model selection hard-coded for now.

### ChatKit Prototype Module
- `src/merak_agent/workflows/chatkit_server.py` *(new)*
  - Instantiate `MemoryStore` and reuse `create_trip_planner_agent()`.
  - Use `Runner.run_streamed` and `stream_agent_response` to bridge responses.
  - Leave attachment support as an explicit TODO.

### Prototype Runner
- `scripts/run_chatkit_prototype.py` *(new)*
  - FastAPI app exposing `/chatkit` (POST) and optional `/healthz`.
  - Accept simple `--host` and `--port` flags; print curl guidance for manual tests on startup.

### Manual Validation
- Document in-script steps to:
  1. Start the server.
  2. Send a sample Trip Planner request via curl or the ChatKit client.
  3. Verify streamed responses land without errors.

## Follow-Up (After Prototype Success)
- Expand README and `.agent/System/project_architecture.md` with ChatKit details.
- Add automated tests, Makefile targets, persistent storage, attachment handling, and broader configuration if we promote beyond prototype.
