"""
Contains functions to validate scenario and sector data
"""

# NOTE(RKM 2019-12-28) We don't currently validate any internal references in the
# scenario data. I.e. we don't check that a fix referenced by name actually exists in
# another part of the schema

import json
from typing import Union

from aviary.sector.sector_element import SectorElement
from jsonschema import validate


_SECTOR_SCHEMA = {
    "type": "object",
    "properties": {
        "features": {"type": "array", "items": {"$ref": "#/definitions/feature"}},
        "type": {"type": "string"},
        # NOTE(RKM 2019-12-28) Only used for debugging
        "_source": {"type": "string"},
    },
    "required": ["features", "type"],
    "additionalProperties": False,
    "definitions": {
        "feature": {
            "type": "object",
            "properties": {
                "properties": {"$ref": "#/definitions/properties"},
                "type": {"type": "string"},
                "geometry": {"$ref": "#/definitions/geometry"},
            },
            "required": ["properties", "type", "geometry"],
            "additionalProperties": False,
        },
        "properties": {
            "type": "object",
            "properties": {
                "airway_width_nm": {"type": "number"},
                "length_nm": {"type": "number"},
                "name": {"type": "string"},
                "offset_nm": {"type": "number"},
                "type": {"type": "string"},
                "children": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": True,
                },
                "shape": {"type": "string"},
                "origin": {"type": "array", "items": {"type": "number"}},
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


def validate_geojson_sector(geojson: dict) -> Union[SectorElement, str]:
    try:
        validate(instance=geojson, schema=_SECTOR_SCHEMA)
        # TODO (RKM 2019-12-20) Check what exceptions this can throw
        return SectorElement.deserialise(json.dumps(geojson))
    except Exception as exc:
        return str(exc)
