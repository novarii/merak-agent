# Merak Trip Planner – System Overview

## Project Goal
Provide a minimal, local-friendly example of an OpenAI Agents SDK powered trip-planning assistant. The agent produces grounded 3-day itineraries by combining curated destination data with LLM reasoning, making it easy for contributors to extend catalog coverage, plug in new tools, or adopt the Runner orchestration pattern in their own projects.

## Tech Stack
- **Runtime:** Python 3.11
- **LLM Orchestration:** [OpenAI Agents Python SDK (`openai-agents`)](https://openai.github.io/openai-agents-python/)
- **Packaging:** `pyproject.toml` (PEP 621) + editable installs for local development
- **Testing:** `pytest` with `pytest-cov` (configured via `pyproject.toml`)
- **Lint/Format:** `ruff` defaults defined in `pyproject.toml`
- **Documentation:** `.agents` workspace for internal guides and PRDs

## Code Layout
- `src/merak_agent/agents/trip_planner.py` – Factory for the `TripPlanner` agent, including persona instructions that enforce pre-flight clarification, tool usage, and markdown itinerary formatting.
- `src/merak_agent/tools/destination_lookup.py` – `@function_tool` implementation that scores curated destinations against traveler preferences and returns structured context for the LLM.
- `src/merak_agent/common/destinations.py` – Immutable catalog of `Destination` dataclasses describing regions, best seasons, highlights, cuisine themes, and practical tips.
- `scripts/run_trip_planner.py` – Async CLI harness that reads a user prompt, ensures `OPENAI_API_KEY` is set, then executes the agent with `Runner.run`.
- `tests/agents/test_trip_planner_agent.py` & `tests/tools/test_destination_lookup.py` – Unit tests covering agent wiring and tool validation/guard-rails.
- `requirements.txt` / `pyproject.toml` – Declare runtime dependencies (`openai-agents`, `typing_extensions`, `pytest`, `pytest-cov`) and lint settings.

## Execution Flow
1. **Entry Point:** Developer runs `python scripts/run_trip_planner.py "<trip request>"`.
2. **Agent Assembly:** `create_trip_planner_agent()` instantiates an `agents.Agent` with rich instructions and attaches `lookup_destination`.
3. **Orchestration:** The script calls `Runner.run(agent, prompt)` to execute the agent workflow asynchronously.
4. **Tooling:** When the LLM decides to ground recommendations, the Agents SDK invokes `lookup_destination`, which selects the best match from the local catalog using `_score_destination`.
5. **Response:** The final LLM output is printed as markdown containing overview, daily schedule table, and packing/booking checklist.

## Data & Storage
- **Destination Catalog:** Small in-repo dataset stored in `src/merak_agent/common/destinations.py`. It is immutable (`tuple[Destination, ...]`) and referenced through the helper `iter_catalog()` to keep the data layer simple.
- **Persistence:** No database or external cache. All state lives in memory during a single agent run.
- **Extensibility:** Add new destinations by appending `Destination` entries, keeping `themes`, `best_seasons`, and `practical_tips` populated to ensure meaningful rankings.

## External Integrations
- **OpenAI API:** Authentication via `OPENAI_API_KEY`. The project does not wrap API calls directly; it relies on the Agents SDK abstractions.
- **No other integrations** (e.g., booking APIs, weather services). The lookup tool currently operates solely on the curated catalog, so compliance and failure modes are predictable.

## Configuration & Environment
- Set up the virtual environment with `python -m venv .venv && source .venv/bin/activate`.
- Install dependencies using `pip install -e .` (editable install) or `pip install -r requirements.txt`.
- Export `OPENAI_API_KEY` before running any agent code (the CLI aborts if the variable is missing).
- `typing_extensions>=4.9` is required to satisfy the Agents SDK / Pydantic expectation for `TypedDict` support on Python 3.11.

## Testing & Quality Gates
- Run `pytest` from the project root to execute both agent and tool tests; branch coverage can be inspected via the configured `pytest-cov` flags.
- Add new tests mirroring runtime modules under `tests/` (e.g., `tests/tools/test_<name>.py` for a new tool).
- Ruff configuration in `pyproject.toml` enforces formatting and linting (`ruff check src tests`, `ruff format`).

## Operational Considerations
- The agent is single-turn; repeated executions should be handled via the CLI or by embedding `Runner.run` inside a larger application.
- Error handling in `lookup_destination` raises `ValueError` when traveler preferences are too vague or unmatched, which the Agents SDK surfaces back to the LLM for clarification.
- To trace agent/tool interactions, integrate with the Agents SDK tracing hooks as a future enhancement (not configured yet).

## Related Docs
- [../Tasks/trip_planner.md](../Tasks/trip_planner.md)
- [../../README.md](../../README.md)
