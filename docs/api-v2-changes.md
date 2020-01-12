
# BlueBird v2 API Changes

## General

- Changed the callsign label from "acid" to "callsign" for clarity

## Endpoints added

- `SCENARIO` - Loads a JSON scenario using the new format
- `SECTOR` - Loads a GeoJSON sector using the new format
- `SIMINFO` - Returns the current state of BlueBird and the simulator

## Endpoints removed

- `GET /api/v2/alt` removed. Now covered by `POS`
- `IC` endpoint removed. Now covered by `SECTOR` and `SCENARIO`
- `SIMMODE` endpoint removed. The simulation mode must be set at startup, and can't be
changed
- `VS` (vertical speed) endpoint removed. Can now only set this while issuing a "change
altitude" command
- `DEFWPT` endpoint removed. Waypoints can now only be defined in the initial sector.

## Endpoints renamed

- `SPD` endpoint renamed to `GSPD` for clarity
