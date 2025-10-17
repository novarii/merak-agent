"""Trip planning agent powered by the OpenAI Agents SDK."""

from __future__ import annotations

from agents import Agent

from merak_agent.tools import lookup_destination


TRIP_PLANNER_INSTRUCTIONS = (
    "You are a meticulous travel concierge who crafts practical, 3-day itineraries. "
    "Always gather context about the traveler first (budget, interests, traveling party, "
    "time of year), then call lookup_destination to ground recommendations in curated facts. "
    "Return a markdown itinerary with:\n"
    "- a short overview paragraph;\n"
    "- a table breaking down morning/afternoon/evening plans for each day;\n"
    "- a checklist of booking reminders and packing tips.\n"
    "Stay realistic about pacing, account for transit time, and highlight one food experience "
    "per day."
)


def create_trip_planner_agent() -> Agent:
    """Factory for a trip planning agent that leans on the curated lookup tool."""

    return Agent(
        name="TripPlanner",
        instructions=TRIP_PLANNER_INSTRUCTIONS,
        tools=[lookup_destination],
    )

