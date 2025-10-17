"""Curated travel destination data leveraged by the trip planner agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Destination:
    """Describes a destination that the agent can reference."""

    city: str
    country: str
    region: str
    best_seasons: tuple[str, ...]
    ideal_duration_days: range
    themes: tuple[str, ...]
    description: str
    highlights: tuple[str, ...]
    cuisine_focus: tuple[str, ...]
    practical_tips: tuple[str, ...]


CATALOG: tuple[Destination, ...] = (
    Destination(
        city="Kyoto",
        country="Japan",
        region="Asia",
        best_seasons=("spring", "fall"),
        ideal_duration_days=range(3, 6),
        themes=("culture", "history", "food", "nature"),
        description=(
            "Former imperial capital known for wooden temples, serene gardens, and tea culture."
        ),
        highlights=(
            "Fushimi Inari Taisha at sunrise",
            "Tea ceremony in Gion",
            "Arashiyama bamboo grove",
            "Philosopher's Path stroll",
        ),
        cuisine_focus=("kaiseki", "matcha desserts", "ramen"),
        practical_tips=(
            "Purchase an ICOCA card for transit before arrival in Kyoto Station.",
            "Reserve kaiseki dinners and tea ceremonies at least two weeks ahead.",
        ),
    ),
    Destination(
        city="Lisbon",
        country="Portugal",
        region="Europe",
        best_seasons=("spring", "fall"),
        ideal_duration_days=range(3, 6),
        themes=("culture", "food", "nightlife", "coast"),
        description="Sun-washed coastal city with vibrant food scene and ceramic-covered architecture.",
        highlights=(
            "Tram 28 ride through Alfama",
            "Day trip to Sintra palaces",
            "Belém tower and pasteis tasting",
            "Sunset at Miradouro da Senhora do Monte",
        ),
        cuisine_focus=("seafood", "petiscos", "pastel de nata"),
        practical_tips=(
            "Wear comfortable shoes; old town streets are steep and cobblestoned.",
            "Purchase a Viva Viagem card to use metro, trams, and ferries.",
        ),
    ),
    Destination(
        city="Reykjavík",
        country="Iceland",
        region="Europe",
        best_seasons=("summer",),
        ideal_duration_days=range(4, 8),
        themes=("nature", "adventure", "wellness"),
        description="Compact capital that doubles as a launch pad for geothermal spas and volcanic landscapes.",
        highlights=(
            "Golden Circle self-drive tour",
            "Blue Lagoon or Sky Lagoon soak",
            "Whale watching from the harbor",
            "Day trip along the South Coast waterfalls",
        ),
        cuisine_focus=("lamb", "seafood", "skyr"),
        practical_tips=(
            "Rent a car with gravel protection insurance for longer excursions.",
            "Pack layers; weather shifts rapidly even in summer.",
        ),
    ),
    Destination(
        city="Mexico City",
        country="Mexico",
        region="Americas",
        best_seasons=("spring", "fall"),
        ideal_duration_days=range(4, 8),
        themes=("culture", "food", "art"),
        description="Energetic metropolis with world-class museums, mercados, and modern dining.",
        highlights=(
            "Frida Kahlo Museum and Coyoacán walk",
            "Street food tour in Roma",
            "Sunrise hot air balloon over Teotihuacán",
            "Floating trajinera in Xochimilco",
        ),
        cuisine_focus=("tacos al pastor", "mole", "mezcal tastings"),
        practical_tips=(
            "Use authorized taxis or ride-share at night for safer transportation.",
            "Acclimate slowly to altitude; stay hydrated on day one.",
        ),
    ),
    Destination(
        city="Queenstown",
        country="New Zealand",
        region="Oceania",
        best_seasons=("summer", "fall"),
        ideal_duration_days=range(4, 7),
        themes=("adventure", "nature"),
        description="Adventure capital surrounded by glacial lakes and alpine peaks.",
        highlights=(
            "Milford Sound day cruise",
            "Glenorchy scenic drive",
            "Arrowtown wine tasting",
            "Ben Lomond summit hike",
        ),
        cuisine_focus=("pinot noir", "Fergburger", "lamb"),
        practical_tips=(
            "Book adventure activities at least a week ahead in high season.",
            "Consider driving; roads are well maintained yet winding—plan extra time.",
        ),
    ),
)


def iter_catalog() -> Iterable[Destination]:
    """Convenience helper for iterating over the immutable catalog."""

    return iter(CATALOG)

