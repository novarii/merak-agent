"""Tooling for surfacing destination context to the trip planning agent."""

from __future__ import annotations

from typing_extensions import TypedDict

from agents import function_tool

from merak_agent.common.destinations import Destination, iter_catalog


class TripPreferences(TypedDict, total=False):
    """Schema for user preferences supplied to the lookup tool."""

    destination: str
    region: str
    season: str
    interests: list[str]
    trip_length_days: int


class DestinationRecommendation(TypedDict):
    """Structured response returned by the lookup tool."""

    city: str
    country: str
    summary: str
    recommended_trip_length_days: str
    best_seasons: list[str]
    aligned_themes: list[str]
    highlights: list[str]
    cuisine_focus: list[str]
    practical_tips: list[str]


def _score_destination(preferences: TripPreferences, destination: Destination) -> int:
    """Score how well a destination aligns with the provided preferences."""

    score = 0
    destination_name = preferences.get("destination")
    if destination_name:
        if destination_name.lower() == destination.city.lower():
            score += 5
        elif destination_name.lower() in f"{destination.city.lower()}, {destination.country.lower()}":
            score += 3

    region = preferences.get("region")
    if region and region.lower() == destination.region.lower():
        score += 2

    season = preferences.get("season")
    if season and season.lower() in destination.best_seasons:
        score += 2

    interests = preferences.get("interests", [])
    if interests:
        score += len(set(i.lower() for i in interests) & set(destination.themes))

    trip_length = preferences.get("trip_length_days")
    if trip_length and trip_length in destination.ideal_duration_days:
        score += 2

    return score


def _format_trip_length(destination: Destination) -> str:
    """Render the ideal duration range as a friendly string."""

    values = sorted(destination.ideal_duration_days)
    if not values:
        return "N/A"

    return f"{values[0]}-{values[-1]} days"


@function_tool
def lookup_destination(preferences: TripPreferences) -> DestinationRecommendation:
    """Retrieve curated context for a destination that fits the traveler's preferences."""

    if not preferences:
        raise ValueError("At least one preference (season, region, or interests) must be provided.")

    candidates = list(iter_catalog())
    ranked = sorted(
        candidates,
        key=lambda destination: _score_destination(preferences, destination),
        reverse=True,
    )

    top_match = ranked[0]
    if _score_destination(preferences, top_match) == 0:
        raise ValueError(
            "Unable to find a destination that aligns with the supplied preferences."
        )

    return DestinationRecommendation(
        city=top_match.city,
        country=top_match.country,
        summary=top_match.description,
        recommended_trip_length_days=_format_trip_length(top_match),
        best_seasons=list(top_match.best_seasons),
        aligned_themes=list(top_match.themes),
        highlights=list(top_match.highlights),
        cuisine_focus=list(top_match.cuisine_focus),
        practical_tips=list(top_match.practical_tips),
    )
