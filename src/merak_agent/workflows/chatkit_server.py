"""ChatKit server shim that bridges the Trip Planner agent to ChatKit clients."""

from __future__ import annotations

from pathlib import Path
from typing import Any, AsyncIterator, Dict, Optional

from agents import Runner
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from chatkit.server import ChatKitServer, ThreadStreamEvent
from chatkit.types import ThreadMetadata, UserMessageItem

from merak_agent.agents import create_trip_planner_agent

RequestContext = Dict[str, Any]

try:  # pragma: no cover - import path differs between library versions.
    from chatkit.stores import AttachmentStore as _AttachmentStoreBase
    from chatkit.stores.sqlite import SQLiteStore
except ImportError:  # pragma: no cover
    try:
        from chatkit.store import AttachmentStore as _AttachmentStoreBase
        from chatkit.store.sqlite import SQLiteStore
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "Unable to import ChatKit store implementations. Ensure openai-chatkit is installed."
        ) from exc


class DisabledAttachmentStore(_AttachmentStoreBase[RequestContext]):  # type: ignore[type-arg]
    """Attachment store placeholder that documents unsupported operations."""

    async def delete_attachment(self, attachment_id: str, context: RequestContext) -> None:
        raise NotImplementedError("Attachment deletion is not yet supported for the ChatKit server.")

    async def create_attachment(self, input: Any, context: RequestContext) -> Any:
        raise NotImplementedError("Attachment uploads are not yet supported for the ChatKit server.")

    def generate_attachment_id(self, mime_type: str, context: RequestContext) -> str:
        raise NotImplementedError("Attachment ID generation is not yet supported for the ChatKit server.")


class TripPlannerChatKitServer(ChatKitServer[RequestContext]):
    """Minimal ChatKit server adapter for the Trip Planner agent."""

    DEFAULT_DB_FILENAME = "chatkit_threads.sqlite3"

    def __init__(self, database_path: Optional[str | Path] = None) -> None:
        store_path = self._ensure_database_path(database_path)
        store = SQLiteStore(str(store_path))
        super().__init__(store, attachment_store=DisabledAttachmentStore())
        self._agent = create_trip_planner_agent()
        self._store_path = store_path

    @classmethod
    def _ensure_database_path(cls, database_path: Optional[str | Path]) -> Path:
        """Return an absolute SQLite path and ensure its parent directory exists."""

        if database_path:
            path = Path(database_path)
        else:
            path = Path(".merak") / cls.DEFAULT_DB_FILENAME

        path = path.expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Stream ChatKit events generated from the Trip Planner agent.

        The context dict carries request metadata (e.g., userId/clientHost) forwarded by
        the FastAPI layer so that future permission checks have access to the caller.
        """

        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

        agent_input = []
        if input_user_message is not None:
            agent_input = await simple_to_agent_input(input_user_message)

        result = Runner.run_streamed(
            self._agent,
            agent_input,
            context=agent_context,
        )

        async for event in stream_agent_response(agent_context, result):
            yield event
