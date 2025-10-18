"""Reusable chat loop helpers for console-based agent interactions."""

from __future__ import annotations

from collections import deque
from typing import Any, Awaitable, Callable, Iterable, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - used for static analysis only
    from agents import Agent
else:  # pragma: no cover - fallback when type checking is disabled
    Agent = Any

RunCoroutine = Callable[[Agent, str, Any], Awaitable[Any]]

DEFAULT_EXIT_COMMANDS = ("exit", "quit")
_EXIT_MESSAGE = "\nEnding chat.\n"


async def run_interactive_chat(
    agent: Agent,
    session: Any,
    read_input: Callable[[], str],
    write_output: Callable[[str], None],
    *,
    runner: RunCoroutine,
    initial_prompt: str | None = None,
    exit_commands: Iterable[str] | None = None,
) -> None:
    """Drive a multi-turn chat loop against the provided `runner`.

    Args:
        agent: Agent instance to execute for each user prompt.
        session: Conversation session shared across turns.
        read_input: Callable that returns the next user message (synchronous).
        write_output: Callable that renders agent output to the caller's interface.
        runner: Awaitable that executes the agent (e.g., `Runner.run`).
        initial_prompt: Optional first user message to enqueue before reading input.
        exit_commands: Iterable of commands that end the chat (case-insensitive).
    """

    exit_phrases = {cmd.lower() for cmd in (exit_commands or DEFAULT_EXIT_COMMANDS)}
    pending = deque()
    if initial_prompt:
        pending.append(initial_prompt)

    while True:
        if pending:
            raw_prompt = pending.popleft()
        else:
            try:
                raw_prompt = read_input()
            except EOFError:
                write_output(_EXIT_MESSAGE)
                break
            except KeyboardInterrupt:
                write_output(_EXIT_MESSAGE)
                break

        prompt = (raw_prompt or "").strip()
        if not prompt:
            continue

        if prompt.lower() in exit_phrases:
            write_output(_EXIT_MESSAGE)
            break

        try:
            result = await runner(agent, prompt, session=session)
        except Exception as exc:  # pragma: no cover - defensive for unexpected SDK errors
            write_output(f"\n[error] {exc}\n")
            continue

        output = getattr(result, "final_output", None)
        if output is None:
            output = str(result)

        write_output("\nAgent:\n")
        write_output(f"{output}\n")
