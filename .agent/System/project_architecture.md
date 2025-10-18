# Project Architecture

## Overview
Merak Agent is a Python 3.11 project that delivers a travel-planning conversational agent using the OpenAI Agents Python SDK. The goal is to gather a traveler’s context, score a curated destination catalog, and surface a structured three-day itinerary through an interactive CLI.

## Codebase Layout
- `src/merak_agent/agents/`: Agent factories. `trip_planner.py` declares the `TripPlanner` agent and its instructions.
- `src/merak_agent/tools/`: Tool definitions the agent can call. `destination_lookup.py` implements the scoring and formatting logic for travel recommendations.
- `src/merak_agent/common/`: Shared utilities and datasets. `destinations.py` stores immutable destination metadata consumed by the lookup tool.
- `src/merak_agent/workflows/`: Reusable workflows such as the asynchronous REPL loop in `chat_cli.py`.
- `scripts/`: Entry points and automation. `run_trip_planner.py` wires the CLI to the agent runtime.
- `assets/`: Reserved for persisted prompts; currently empty but maintained for future prompt templates.
- `tests/`: Pytest suites mirroring the runtime package layout.

## Runtime Flow
1. A user launches `python3 scripts/run_trip_planner.py`, optionally supplying an opening prompt or `--single-turn`.
2. The script instantiates the `TripPlanner` agent, prepares a `SQLiteSession`, and delegates execution to either a single-turn runner or the interactive REPL in `run_interactive_chat`.
3. Each call to `Runner.run` (OpenAI Agents SDK) invokes the LLM instructions and enables tool-calling. The agent requests destination context via the `lookup_destination` tool when crafting an itinerary.
4. Tool execution filters the curated catalog, returning structured recommendations that the agent converts into a markdown itinerary for display in the CLI.

## Agent Definition (`src/merak_agent/agents/trip_planner.py`)
- Wraps `TRIP_PLANNER_INSTRUCTIONS`, emphasizing user context gathering, calling `lookup_destination`, and returning formatted itineraries.
- Registers the tool list with the OpenAI Agents SDK by returning an `Agent` instance (`agents.Agent`) configured for the CLI workflow.

## Tooling (`src/merak_agent/tools/destination_lookup.py`)
- `TripPreferences` and `DestinationRecommendation` typed dicts define the tool input/output schema exposed to the agent runtime.
- `_score_destination` ranks catalog entries using traveler hints (name, region, season, interests, preferred duration).
- `_format_trip_length` renders duration ranges for human-readable responses.
- `lookup_destination` (decorated with `agents.function_tool`) enforces minimum preference input, sorts candidates by score, and returns the best-aligned destination. It raises `ValueError` when insufficient context or no viable match is found—surfacing clear feedback to the agent.

## Data Catalog (`src/merak_agent/common/destinations.py`)
- Defines an immutable `Destination` dataclass capturing city metadata, seasons, themes, highlights, cuisine focus, and practical tips.
- Exposes `CATALOG`, a tuple of predefined destinations, and `iter_catalog()` for iteration without mutating the source data.
- Serves as the sole knowledge base behind `lookup_destination`; expanding the catalog (or switching to a persistent datastore) only requires touching this module.

## Workflow Layer (`src/merak_agent/workflows/chat_cli.py`)
- `run_interactive_chat` coordinates asynchronous multi-turn dialogue, buffering prompts, filtering blank input, honoring exit commands, and streaming agent output.
- Accepts an injected runner coroutine (the project uses `Runner.run`), keeping the workflow decoupled from the SDK implementation.
- Gracefully handles EOF, `KeyboardInterrupt`, and tool/agent exceptions by surfacing user-friendly messages.

## CLI Entry Point (`scripts/run_trip_planner.py`)
- Parses CLI arguments, supports single-turn and interactive modes, and validates the `OPENAI_API_KEY` environment variable before execution.
- Builds a `SQLiteSession` from the Agents SDK, defaulting to in-memory storage when no `--session-id` is provided.
- Runs single-turn requests directly or delegates to the REPL workflow for multi-turn chats.
- Highlights the SDK’s session-handling behavior documented in the [OpenAI Agents Python docs](https://github.com/openai/openai-agents-python) (see sessions and runner usage guidance consulted via Context7).

## Persistence & Database Considerations
- The application itself does not define custom database tables. Conversation history is managed by `agents.SQLiteSession`, which persists turns to SQLite when given a concrete session identifier.
- The curated destination catalog is an in-code immutable tuple. There is no runtime mutation or external data store.
- Future expansion to an external database would require introducing repository layers around `lookup_destination` while preserving the public tool signature.

## External Integrations
- **OpenAI Agents Python SDK (`agents.Agent`, `Runner`, `SQLiteSession`, `function_tool`)** – orchestrates LLM execution, tool-calling, and session persistence. Refer to the sessions and usage patterns reviewed in the live documentation for details on `Runner.run` and session-scoped usage metrics.
- **OpenAI ChatKit** – available as a dependency for advanced conversation management but not yet invoked in code.
- **FastAPI / Uvicorn / httpx** – present in dependencies for eventual API surfacing or network operations; currently unused within the runtime modules.
- **python-dotenv** – available for environment management though not explicitly imported yet.

## Configuration & Operations
- Requires `OPENAI_API_KEY` to run; the CLI exits early if the variable is missing.
- Python version: 3.11 (enforced by `pyproject.toml` and repo guidelines).
- Recommended developer flow: create a virtual environment, install `requirements.txt`, then run `pytest` or `python3 scripts/run_trip_planner.py`.
- `run_interactive_chat` supports exit commands (`exit`, `quit`) and handles blank input gracefully, making it safe for terminal usage.

## Testing & Quality
- Pytest suites cover agent wiring, tool behavior (including error handling), and the CLI workflow loop.
- Coverage configuration (`--cov=src --cov-report=term-missing`) enforces measurement across the runtime package.
- Ruff (lint/format) is configured for PEP 8 compliance with 100-character lines and double-quoted strings.

## Extension Breakpoints
- Add new agents in `src/merak_agent/agents/` and mirror tests in `tests/agents/`.
- Introduce additional tools under `src/merak_agent/tools/`, ensuring matching tests and explicit exports in `__init__.py`.
- Persist prompt templates in `assets/prompts/` with a `.j2` suffix to keep them organized.

## Related Docs
- [../README.md](../README.md) – index of internal documentation and onboarding pointers.
- [../../README.md](../../README.md) – repository quickstart and CLI usage.
