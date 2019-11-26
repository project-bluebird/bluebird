"""
Contains functions to validate scenario and sector data
"""

# TODO(RKM 2019-11-26) Should we attempt to validate that the schema is self-consistent?
# (i.e. all children of properties refer to other properties in the data)

from typing import Optional


from jsonschema import validate
from jsonschema.exceptions import ValidationError


_SECTOR_SCHEMA = {
    "type": "object",
    "properties": {
        "features": {"type": "array", "items": {"$ref": "#/definitions/feature"}}
    },
    "additionalProperties": False,
    "definitions": {
        "feature": {
            "type": "object",
            "properties": {
                "properties": {"$ref": "#/definitions/properties"},
                "type": {"type": "string"},
                "geometry": {"$ref": "#/definitions/geometry"},
            },
            "additionalProperties": False,
        },
        "properties": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "type": {"type": "string"},
                "children": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": True,  # See comment at top of module
                },
                "lower_limit": {"type": "integer", "optional": True},
                "upper_limit": {"type": "integer", "optional": True},
            },
            "additionalProperties": False,
        },
        "geometry": {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                # TODO(RKM 2019-11-26) Probably a better way of doing this
                "coordinates": {
                    "type": "array",
                    "items": {"type": ["number", "array"]},
                },
            },
            "additionalProperties": False,
        },
    },
}


def validate_geojson_sector(data: dict) -> Optional[str]:
    try:
        return validate(instance=data, schema=_SECTOR_SCHEMA)
    except ValidationError as exc:
        return str(exc)
