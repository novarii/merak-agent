"""Tests for the interactive chat workflow helpers."""

from __future__ import annotations

from typing import Optional

import pytest

from merak_agent.workflows import run_interactive_chat


class _Result:
    def __init__(self, text: str) -> None:
        self.final_output = text


@pytest.mark.asyncio
async def test_run_interactive_chat_handles_initial_prompt_and_exit() -> None:
    outputs: list[str] = []
    calls: list[str] = []

    async def runner(agent: object, prompt: str, session: Optional[object] = None) -> _Result:
        calls.append(prompt)
        return _Result(f"reply:{prompt}")

    inputs = iter(["follow up", "exit"])

    def read() -> str:
        return next(inputs)

    def write(message: str) -> None:
        outputs.append(message)

    await run_interactive_chat(
        agent=object(),
        session=object(),
        read_input=read,
        write_output=write,
        runner=runner,
        initial_prompt="first turn",
    )

    assert calls == ["first turn", "follow up"]
    assert outputs.count("\nAgent:\n") == 2
    assert outputs[-1] == "\nEnding chat.\n"
    assert outputs[-2] == "reply:follow up\n"


@pytest.mark.asyncio
async def test_run_interactive_chat_skips_blank_entries() -> None:
    outputs: list[str] = []
    calls: list[str] = []

    async def runner(agent: object, prompt: str, session: Optional[object] = None) -> _Result:
        calls.append(prompt)
        return _Result(prompt)

    inputs = iter(["", "   ", "exit"])

    def read() -> str:
        return next(inputs)

    def write(message: str) -> None:
        outputs.append(message)

    await run_interactive_chat(
        agent=object(),
        session=object(),
        read_input=read,
        write_output=write,
        runner=runner,
    )

    assert calls == []
    assert outputs == ["\nEnding chat.\n"]


@pytest.mark.asyncio
async def test_run_interactive_chat_reports_runner_errors() -> None:
    outputs: list[str] = []

    async def runner(agent: object, prompt: str, session: Optional[object] = None) -> _Result:
        raise RuntimeError("boom")

    inputs = iter(["tokyo trip", "exit"])

    def read() -> str:
        return next(inputs)

    def write(message: str) -> None:
        outputs.append(message)

    await run_interactive_chat(
        agent=object(),
        session=object(),
        read_input=read,
        write_output=write,
        runner=runner,
    )

    assert any("[error]" in message for message in outputs)
    assert outputs[-1] == "\nEnding chat.\n"
