# Trip Planner Agent

## Problem / Goal
Create an initial OpenAI Agents SDK integration that can propose a grounded multi-day travel itinerary. This serves as a foundation for future workflow expansion.

## Solution Overview
- Track curated destination knowledge locally and expose it through an `lookup_destination` tool.
- Configure a single `TripPlanner` agent that relies on the tool and produces structured itineraries.
- Provide a CLI runner so contributors can trigger the agent with their own prompts.
- Supply basic tests that validate configuration and tool behaviour without calling the OpenAI API.

## Non-Goals
- Real-time voice experiences.
- External travel APIs or live pricing data.
- Persistent conversation memory across sessions.

## Notes
- The agent instructions emphasise gathering traveler context first; follow-up prompts improve quality.
- Extend the catalog in `src/merak_agent/common/destinations.py` to broaden coverage.

## Open Bug: TypedDict Import Error (Python 3.11)

### Context
- Running `scripts/run_trip_planner.py` on Python 3.11 raises `pydantic.errors.PydanticUserError: Please use typing_extensions.TypedDict instead of typing.TypedDict on Python < 3.12.`
- Pydantic's [standard library types guide](https://docs.pydantic.dev/latest/api/standard_library_types/) notes that Python 3.12 and lower must import `TypedDict` from `typing_extensions` for validation.

### Fix Plan
1. **Update imports in `src/merak_agent/tools/destination_lookup.py`:** swap `from typing import TypedDict` for `from typing_extensions import TypedDict` to align with the documented requirement.
2. **Declare dependency:** add `typing_extensions>=4.9` to `pyproject.toml` and `requirements.txt` so the package is available in all environments.
3. **Run test suite:** execute `pytest` to confirm the lookup tool schema builds correctly after the change.
4. **Document resolution:** note the compatibility detail in README troubleshooting once verified.
