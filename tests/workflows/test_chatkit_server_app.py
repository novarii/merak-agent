"""Tests for the ChatKit FastAPI application factory."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

import scripts.run_chatkit_server as server_module


class DummyServer:
    """Stub ChatKit server used to verify FastAPI wiring."""

    def __init__(self, result: Any) -> None:
        self._result = result
        self.calls: list[tuple[bytes, dict[str, Any]]] = []

    async def process(self, payload: bytes, context: dict[str, Any]) -> Any:
        self.calls.append((payload, context))
        return self._result


def test_chatkit_endpoint_passes_user_context(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure the HTTP handler forwards user identity and request metadata."""

    server = DummyServer(SimpleNamespace(json="{}"))
    app = server_module.build_app(server)
    client = TestClient(app)

    response = client.post(
        "/chatkit",
        json={"type": "noop"},
        headers={"X-User-Id": "traveler_123"},
    )

    assert response.status_code == 200
    assert server.calls, "process() should be invoked once"

    payload, context = server.calls[0]
    assert payload, "payload should contain the serialized request body"
    assert context["userId"] == "traveler_123"
    assert context["request"]


def test_chatkit_endpoint_streams_results(monkeypatch: pytest.MonkeyPatch) -> None:
    """StreamingResult responses should be surfaced as text/event-stream."""

    # Substitute StreamingResult with a lightweight async iterator for the test.
    class FakeStream:
        async def __aiter__(self):
            yield b"data: test\n\n"

    monkeypatch.setattr(server_module, "StreamingResult", FakeStream)

    server = DummyServer(FakeStream())
    app = server_module.build_app(server)
    client = TestClient(app)

    with client.stream("POST", "/chatkit", json={"type": "noop"}) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")

        chunks = list(response.iter_text())
        assert any("data: test" in chunk for chunk in chunks)

    assert server.calls, "process() should be invoked once for streaming responses"


def test_healthz_endpoint() -> None:
    """The health check should return a simple ok payload."""

    server = DummyServer(SimpleNamespace(json="{}"))
    app = server_module.build_app(server)
    client = TestClient(app)

    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
