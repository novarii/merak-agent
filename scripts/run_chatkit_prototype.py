"""Run the Trip Planner ChatKit prototype server."""

from __future__ import annotations

import argparse
import os
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import Response, StreamingResponse
import uvicorn

from chatkit.server import StreamingResult

from merak_agent.workflows import TripPlannerChatKitServer


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Launch a minimal FastAPI server that exposes the Trip Planner through ChatKit.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Interface to bind (default: 127.0.0.1).")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000).")
    return parser.parse_args(argv)


def _build_app(server: TripPlannerChatKitServer) -> FastAPI:
    app = FastAPI(title="Merak Trip Planner ChatKit Prototype")

    @app.post("/chatkit")
    async def chatkit_endpoint(request: Request) -> Response:
        payload = await request.body()
        result = await server.process(payload, {"request": request})

        if isinstance(result, StreamingResult):
            return StreamingResponse(result, media_type="text/event-stream")

        body = getattr(result, "json", "{}")
        return Response(content=body, media_type="application/json")

    @app.get("/healthz")
    async def healthz() -> dict[str, Any]:
        return {"status": "ok"}

    return app


def _print_instructions(host: str, port: int) -> None:
    endpoint = f"http://{host}:{port}/chatkit"
    print(
        "\nChatKit prototype server ready.\n"
        "Manual verification steps:\n"
        "1. Ensure OPENAI_API_KEY is exported in your shell.\n"
        "2. Use a ChatKit client (CLI or web sample) and point it at:\n"
        f"     {endpoint}\n"
        "3. Or send a raw request via curl (replace the trip text as needed):\n"
        "     curl -N \\\n"
        f"       -X POST {endpoint} \\\n"
        "       -H 'Content-Type: application/json' \\\n"
        "       -d '{\n"
        '            \"type\": \"threads.create\",\n'
        '            \"params\": {\n'
        '              \"input\": {\n'
        '                \"content\": [\n'
        '                  {\"type\": \"input_text\", \"text\": \"Plan a relaxed 3-day trip to Lisbon in March.\"}\n'
        '                ],\n'
        '                \"attachments\": [],\n'
        '                \"inference_options\": {\"model\": \"gpt-4.1-mini\"}\n'
        "              }\n"
        "            }\n"
        "          }'\n"
        "4. Watch the terminal for streamed events and ensure the Trip Planner emits an itinerary.\n"
    )


def main(argv: list[str] | None = None) -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY environment variable is required to run the ChatKit prototype.")

    args = _parse_args(argv)
    server = TripPlannerChatKitServer()
    app = _build_app(server)

    _print_instructions(args.host, args.port)
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
