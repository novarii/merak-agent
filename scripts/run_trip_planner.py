"""CLI helper to run the TripPlanner agent via the OpenAI Agents SDK."""

from __future__ import annotations

import asyncio
import os
import sys
from typing import Optional

from agents import Runner

from merak_agent.agents import create_trip_planner_agent


def _read_user_request() -> Optional[str]:
    """Gather the travel request from CLI arguments or stdin."""

    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()

    print("Enter a short description of your trip (press Ctrl+D when finished):")
    try:
        content = sys.stdin.read().strip()
    except KeyboardInterrupt:
        return None

    return content or None


async def _execute(prompt: str) -> None:
    agent = create_trip_planner_agent()
    result = await Runner.run(agent, prompt)
    print("\n=== Trip Planner Response ===\n")
    print(result.final_output)


def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY environment variable must be set before running the agent.")

    prompt = _read_user_request()
    if not prompt:
        raise SystemExit("No trip request provided.")

    asyncio.run(_execute(prompt))


if __name__ == "__main__":
    main()

