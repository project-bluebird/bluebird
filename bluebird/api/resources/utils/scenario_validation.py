"""
Contains functions to validate scenario and sector data
"""

import re
import traceback
from typing import Optional

_START_TIME_RE = re.compile(r"\d{2}:\d{2}:\d{2}")

_SCENARIO_KEYS = ["startTime", "aircraft"]
_AIRCRAFT_KEYS = [
    "callsign",
    "type",
    "departure",
    "destination",
    "startPosition",
    "startTime",
    "currentFlightLevel",
    "clearedFlightLevel",
    "requestedFlightLevel",
    "route",
]


def validate_json_scenario(data: dict) -> Optional[str]:
    """Validates a given GeoJSON scenario file"""
    # TODO(RKM 2019-11-24) This doesn't attempt to deal with the weather data
    try:
        assert all(k in data for k in _SCENARIO_KEYS)
        assert _START_TIME_RE.match(data["startTime"])
        aircraft_node = data["aircraft"]
        assert isinstance(aircraft_node, list) and len(aircraft_node)
        for aircraft in aircraft_node:
            assert isinstance(aircraft, dict)
        return None
    except AssertionError:
        return f"Error parsing scenario: {traceback.format_exc()}"


def _validate_json_aircraft(data: dict) -> None:
    raise NotImplementedError


def _validate_json_route(data: list) -> None:
    raise NotImplementedError
