"""Production-ready ChatKit server entrypoint for the Merak Trip Planner."""

from __future__ import annotations

import argparse
import os
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.responses import Response, StreamingResponse
import uvicorn

from chatkit.server import StreamingResult

from merak_agent.workflows import TripPlannerChatKitServer


FEATURE_FLAG_ENV = "MERAK_ENABLE_CHATKIT_SERVER"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000

RequestContext = Dict[str, Any]


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Launch the FastAPI ChatKit bridge for the Merak Trip Planner agent.",
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help="Interface to bind (default: 127.0.0.1).")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to bind (default: 8000).")
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable FastAPI auto-reload (development only).",
    )
    return parser.parse_args(argv)


def _feature_flag_enabled() -> bool:
    value = os.getenv(FEATURE_FLAG_ENV, "")
    return value.lower() in {"1", "true", "yes", "on"}


def _require_environment() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY environment variable is required.")

    if not _feature_flag_enabled():
        raise SystemExit(
            f"Set {FEATURE_FLAG_ENV}=1 to enable the ChatKit server (disabled by default).\n"
            "This prevents accidental exposure while the frontend is under development.",
        )


def _extract_request_context(request: Request) -> RequestContext:
    user_id = request.headers.get("x-user-id") or request.headers.get("x-userid") or "anonymous"
    client_host = request.client.host if request.client else None

    return {
        "request": request,
        "userId": user_id,
        "clientHost": client_host,
    }


def build_app(server: TripPlannerChatKitServer) -> FastAPI:
    """Create a FastAPI app that proxies ChatKit traffic to the Trip Planner agent."""

    app = FastAPI(title="Merak Trip Planner ChatKit Server")

    @app.post("/chatkit")
    async def chatkit_endpoint(request: Request) -> Response:
        payload = await request.body()
        context = _extract_request_context(request)
        result = await server.process(payload, context)

        if isinstance(result, StreamingResult):
            return StreamingResponse(result, media_type="text/event-stream")

        body = getattr(result, "json", "{}")
        return Response(content=body, media_type="application/json")

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    return app


def _print_ready_message(host: str, port: int) -> None:
    endpoint = f"http://{host}:{port}/chatkit"
    print(
        "\nChatKit server ready.\n"
        "Quick verification:\n"
        "1. Ensure OPENAI_API_KEY is exported and MERAK_ENABLE_CHATKIT_SERVER=1.\n"
        "2. Point a ChatKit client (web or CLI) at:\n"
        f"     {endpoint}\n"
        "3. To smoke test manually, run (adjust prompt as needed):\n"
        "     curl -N \\\n"
        f"       -X POST {endpoint} \\\n"
        "       -H 'Content-Type: application/json' \\\n"
        "       -d '{\n"
        '            \"type\": \"threads.create\",\n'
        '            \"params\": {\n'
        '              \"input\": {\n'
        '                \"content\": [\n'
        '                  {\"type\": \"input_text\", \"text\": \"I want a marketing agent\"}\n'
        '                ],\n'
        '                \"attachments\": [],\n'
        '                \"inference_options\": {\"model\": \"gpt-4.1-mini\"}\n'
        "              }\n"
        "            }\n"
        "          }'\n",
        "\nMemory-backed transcript store: resets when the process exits.",
    )


def main(argv: list[str] | None = None) -> None:
    _require_environment()
    args = _parse_args(argv)

    server = TripPlannerChatKitServer()
    app = build_app(server)

    _print_ready_message(args.host, args.port)

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
