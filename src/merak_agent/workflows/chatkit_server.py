"""ChatKit server shim that bridges the Trip Planner agent to ChatKit clients."""

from __future__ import annotations

from typing import Any, AsyncIterator, Dict

from agents import Runner
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from chatkit.server import ChatKitServer, ThreadStreamEvent
from chatkit.store.memory import MemoryStore
from chatkit.types import ThreadMetadata, UserMessageItem

from merak_agent.agents import create_trip_planner_agent

RequestContext = Dict[str, Any]


class TripPlannerChatKitServer(ChatKitServer[RequestContext]):
    """Minimal ChatKit server adapter for the Trip Planner agent."""

    def __init__(self) -> None:
        super().__init__(MemoryStore())
        self._agent = create_trip_planner_agent()

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Stream ChatKit events generated from the Trip Planner agent."""

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
