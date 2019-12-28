"""
Contains functions to validate scenario and sector data
"""

from typing import Optional

from jsonschema import validate
from jsonschema.exceptions import ValidationError


_START_TIME_RE = r"\d{2}:\d{2}:\d{2}"

_SCENARIO_SCHEMA = {
    "type": "object",
    "properties": {
        "aircraft": {"type": "array", "items": {"$ref": "#/definitions/aircraft"}},
        "startTime": {"type": "string", "pattern": _START_TIME_RE},
    },
    "required": ["aircraft", "startTime"],
    "additionalProperties": False,
    "definitions": {
        "aircraft": {
            "type": "object",
            "properties": {
                "callsign": {"type": "string"},
                "clearedFlightLevel": {"type": "integer"},
                "currentFlightLevel": {"type": "integer"},
                "departure": {"type": "string"},
                "destination": {"type": "string"},
                "requestedFlightLevel": {"type": "integer"},
                "route": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/routeItem"},
                },
                "startPosition": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 2,
                    "maxItems": 2,
                },
                "startTime": {"type": "string", "pattern": _START_TIME_RE},
                "timedelta": {"type": "number"},
                "type": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "routeItem": {
            "type": "object",
            "properties": {
                "fixName": {"type": "string"},
                "geometry": {"$ref": "#/definitions/geomItem"},
            },
            "additionalProperties": False,
        },
        "geomItem": {
            "type": "object",
            "properties": {
                "coordinates": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 1,
                },
                "type": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
}


def validate_json_scenario(data: dict) -> Optional[str]:
    try:
        validate(instance=data, schema=_SCENARIO_SCHEMA)
    except ValidationError as exc:
        return str(exc)
