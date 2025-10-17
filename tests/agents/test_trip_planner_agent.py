from merak_agent.agents import create_trip_planner_agent
from merak_agent.tools.destination_lookup import lookup_destination


def test_trip_planner_agent_configuration() -> None:
    agent = create_trip_planner_agent()

    assert agent.name == "TripPlanner"
    assert lookup_destination in agent.tools
    assert "itinerary" in agent.instructions.lower()
