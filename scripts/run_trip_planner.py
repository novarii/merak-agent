"""CLI helper to run the TripPlanner agent via the OpenAI Agents SDK."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from typing import Optional

from agents import Runner, SQLiteSession

from merak_agent.agents import create_trip_planner_agent
from merak_agent.workflows import run_interactive_chat


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Merak Trip Planner agent in interactive chat mode (default) or single-turn mode.",
    )
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Trip request text. In chat mode this seeds the first turn.",
    )
    parser.add_argument(
        "--single-turn",
        action="store_true",
        help="Execute a single-turn request and exit instead of starting the chat REPL.",
    )
    parser.add_argument(
        "--session-id",
        help="Optional identifier for persisting chat history with SQLiteSession.",
    )
    return parser.parse_args(argv)


def _read_user_request_from_stdin() -> Optional[str]:
    """Fallback helper for single-turn prompts read from stdin."""

    print("Enter a short description of your trip (press Ctrl+D when finished):")
    try:
        content = sys.stdin.read().strip()
    except KeyboardInterrupt:
        return None

    return content or None


def _resolve_single_turn_prompt(parts: list[str]) -> Optional[str]:
    if parts:
        prompt = " ".join(parts).strip()
        return prompt or None

    return _read_user_request_from_stdin()


def _prepare_session(session_id: Optional[str]) -> SQLiteSession:
    if session_id:
        return SQLiteSession(session_id)

    # Use an in-memory session when a persistent identifier is not supplied.
    return SQLiteSession(":memory:")


async def _run_single_turn(agent, prompt: str) -> None:
    result = await Runner.run(agent, prompt)
    print("\n=== Trip Planner Response ===\n")
    print(result.final_output)


async def _run_chat_mode(agent, session, initial_prompt: Optional[str]) -> None:
    print("Starting interactive chat. Type 'exit' or 'quit' to finish.")

    def _read() -> str:
        return input("\nYou: ")

    def _write(message: str) -> None:
        print(message, end="", flush=True)

    await run_interactive_chat(
        agent,
        session,
        _read,
        _write,
        runner=Runner.run,
        initial_prompt=initial_prompt,
    )


def main(argv: Optional[list[str]] = None) -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY environment variable must be set before running the agent.")

    args = _parse_args(argv or sys.argv[1:])
    agent = create_trip_planner_agent()

    if args.single_turn:
        prompt = _resolve_single_turn_prompt(args.prompt)
        if not prompt:
            raise SystemExit("No trip request provided.")

        asyncio.run(_run_single_turn(agent, prompt))
        return

    session = _prepare_session(args.session_id)
    initial_prompt = " ".join(args.prompt).strip() or None
    asyncio.run(_run_chat_mode(agent, session, initial_prompt))


if __name__ == "__main__":
    main()
