import pytest

from merak_agent.tools.destination_lookup import lookup_destination


def test_lookup_destination_prefers_named_city() -> None:
    result = lookup_destination({"destination": "Kyoto", "season": "spring"})

    assert result["city"] == "Kyoto"
    assert "Fushimi Inari Taisha" in " ".join(result["highlights"])


def test_lookup_destination_requires_meaningful_preferences() -> None:
    with pytest.raises(ValueError):
        lookup_destination({})


def test_lookup_destination_rejects_when_nothing_matches() -> None:
    with pytest.raises(ValueError):
        lookup_destination({"season": "winter", "region": "Antarctica"})

