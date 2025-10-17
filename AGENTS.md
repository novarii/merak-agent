# Repository Guidelines

## Docs
- We keep all impotant docs in .agent folder and keep them updated. This is the structure:

.agent
- Tasks: PRD & implementation plan for each feature
- System: Document the current state of the system (project structure, tech stack, integration points, database schema, and core functionalities such as agent architecture, LLM layer, etc.)
- SOP: Best practices of execute certain tasks (e.g. how to add a schema migration, how to add a new page route, etc.)
- README.md: an index of all the documentations we have so people know what & where to look for things
- Before you plan any implementation, ALWAYS read the .agent/README first to get context

## Implementation
- ALWAYS look at our local docs when implementing a feature, and if there is information missing, search web docs to find the most recent information on the frameworks we use.
- When planning or implementing any task, you MUST refer to live documentation (with context 7).

## Project Structure & Module Organization
Keep core agent code in `src/merak_agent/` with subpackages for `agents/`, `tools/`, and `workflows/`. Shared utilities live in `src/merak_agent/common/`. Persisted prompts or fixtures belong in `assets/` (e.g., `assets/prompts/hiring.md`). Mirror runtime modules inside `tests/` such that `src/merak_agent/tools/calendar.py` pairs with `tests/tools/test_calendar.py`. Place developer automation inside `scripts/` and make each script idempotent so it can be rerun safely.

## Build, Test, and Development Commands
Use Python 3.11. Bootstrap with `python -m venv .venv && source .venv/bin/activate`. Install dependencies via `pip install -r requirements.txt` once the file is committed; regenerate it after any dependency bump. Run `pytest` for the full suite and `pytest tests/tools/test_calendar.py -k smoke` to target specific agent flows. Lint with `ruff check src tests` and format with `ruff format` (configure in `pyproject.toml`). Provide `make setup`, `make test`, and `make lint` shortcuts in the root `Makefile` when the automation stabilises.

## Coding Style & Naming Conventions
Follow PEP 8 with 4-space indentation. Favour dataclasses or Pydantic models for structured messages. Name files and modules with lowercase underscores (`candidate_matcher.py`). Export only intentional symbols from `__all__`. Prompt templates should end with `.j2` and live under `assets/prompts/`. Keep functions under 50 lines and prefer explicit type hints on public methods.

## Testing Guidelines
Adopt `pytest` with pytest-cov and keep branch coverage ≥85%. Tests mirror the runtime path; use `test_<module>.py` naming. Group agent behaviour tests with the `agent` marker (`pytest -m agent`). Provide contract tests for external APIs and stub them via `tests/stubs/`. Fail fast on flaky network calls by using VCR or responses.

## Commit & Pull Request Guidelines
Use Conventional Commit messages (`feat: add scheduling tool`). Reference issue IDs in the footer when available (`Refs #42`). Each PR must include: summary of behaviour change, checklist of tests run, screenshots or transcripts for UX-facing flows, and notes on follow-up tasks. Request review from at least one fellow agent maintainer and wait for CI to pass before merging.

## Security & Configuration Tips
Store secrets in `.env` files excluded by `.gitignore`; provide safe defaults in `.env.example`. Document any required API keys in `docs/integration.md`. Audit dependencies with `pip-audit` monthly and remediate high-severity findings immediately. Rotate credentials when contributors offboard.
