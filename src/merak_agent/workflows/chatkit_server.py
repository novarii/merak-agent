"""ChatKit server shim that bridges the Trip Planner agent to ChatKit clients."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, AsyncIterator, Dict, List

from agents import Runner
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from chatkit.server import ChatKitServer, ThreadStreamEvent
from chatkit.store import Attachment, NotFoundError, Page, Store
from chatkit.types import ThreadItem, ThreadMetadata, UserMessageItem

from merak_agent.agents import create_trip_planner_agent

RequestContext = Dict[str, Any]


class _InMemoryStore(Store[RequestContext]):
    """Lightweight in-memory store satisfying the ChatKit Store interface.

    Provides enough persistence for local development and automated tests without an
    external database. Threads and items are kept in dictionaries keyed by their IDs.
    """

    def __init__(self) -> None:
        self._threads: Dict[str, ThreadMetadata] = {}
        self._items: Dict[str, List[ThreadItem]] = defaultdict(list)
        self._attachments: Dict[str, Attachment] = {}

    async def load_thread(self, thread_id: str, context: RequestContext) -> ThreadMetadata:
        try:
            return self._threads[thread_id]
        except KeyError as exc:
            raise NotFoundError(f"Thread {thread_id} not found") from exc

    async def save_thread(self, thread: ThreadMetadata, context: RequestContext) -> None:
        self._threads[thread.id] = thread

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: RequestContext,
    ) -> Page[ThreadItem]:
        items = list(self._items.get(thread_id, []))
        ascending = order.lower() != "desc"
        if not ascending:
            items = list(reversed(items))

        if after:
            try:
                index = next(i for i, item in enumerate(items) if getattr(item, "id", None) == after)
                items = items[index + 1 :]
            except StopIteration:
                items = []

        page_items = items[:limit]
        has_more = len(items) > limit
        after_id = page_items[-1].id if has_more and getattr(page_items[-1], "id", None) else None

        return Page(data=page_items, has_more=has_more, after=after_id)

    async def save_attachment(self, attachment: Attachment, context: RequestContext) -> None:
        self._attachments[attachment.id] = attachment

    async def load_attachment(self, attachment_id: str, context: RequestContext) -> Attachment:
        try:
            return self._attachments[attachment_id]
        except KeyError as exc:
            raise NotFoundError(f"Attachment {attachment_id} not found") from exc

    async def delete_attachment(self, attachment_id: str, context: RequestContext) -> None:
        self._attachments.pop(attachment_id, None)

    async def load_threads(
        self,
        limit: int,
        after: str | None,
        order: str,
        context: RequestContext,
    ) -> Page[ThreadMetadata]:
        threads = sorted(
            self._threads.values(),
            key=lambda thread: thread.created_at,
            reverse=order.lower() == "desc",
        )

        if after:
            try:
                index = next(i for i, thread in enumerate(threads) if thread.id == after)
                threads = threads[index + 1 :]
            except StopIteration:
                threads = []

        page_threads = threads[:limit]
        has_more = len(threads) > limit
        after_id = page_threads[-1].id if has_more else None

        return Page(data=page_threads, has_more=has_more, after=after_id)

    async def add_thread_item(self, thread_id: str, item: ThreadItem, context: RequestContext) -> None:
        self._items[thread_id].append(item)

    async def save_item(self, thread_id: str, item: ThreadItem, context: RequestContext) -> None:
        items = self._items.get(thread_id)
        if not items:
            raise NotFoundError(f"Thread {thread_id} has no items")

        for idx, existing in enumerate(items):
            if getattr(existing, "id", None) == getattr(item, "id", None):
                items[idx] = item
                break
        else:
            raise NotFoundError(f"Item {getattr(item, 'id', '?')} not found in thread {thread_id}")

    async def load_item(self, thread_id: str, item_id: str, context: RequestContext) -> ThreadItem:
        items = self._items.get(thread_id, [])
        for item in items:
            if getattr(item, "id", None) == item_id:
                return item
        raise NotFoundError(f"Item {item_id} not found in thread {thread_id}")

    async def delete_thread(self, thread_id: str, context: RequestContext) -> None:
        self._threads.pop(thread_id, None)
        self._items.pop(thread_id, None)

    async def delete_thread_item(self, thread_id: str, item_id: str, context: RequestContext) -> None:
        items = self._items.get(thread_id)
        if not items:
            return

        self._items[thread_id] = [item for item in items if getattr(item, "id", None) != item_id]


class TripPlannerChatKitServer(ChatKitServer[RequestContext]):
    """Minimal ChatKit server adapter for the Trip Planner agent."""

    def __init__(self) -> None:
        super().__init__(_InMemoryStore())
        self._agent = create_trip_planner_agent()

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
