
# BlueBird Metrics

Configuration values for these can be set in [this](../bluebird/metrics/bluebird/config.py) config file. The two warning distances are configurable, however the minimum distances should be left constant.

## Aircraft Separation

Name: `aircraft_separation`

Description: Returns a value representing the separation "score" between two aircraft.

Configuration parameters:
- `LOS_SCORE` - Score below the minimum separation
- `VERT_MIN_DIST` - Minimum vertical distance (should be constant)
- `VERT_WARN_DIST` - Vertical warning distance
- `HOR_MIN_DIST` - Minimum horizontal distance (should be constant)
- `HOR_WARN_DIST` - Horizontal warning distance

Function: [aircraft_separation(acid1, acid2)](../bluebird/metrics/bluebird/metrics.py)

Parameters: IDs of two aircraft which exist in the simulation
