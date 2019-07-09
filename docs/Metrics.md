
# BlueBird Metrics

Configuration values for these can be set in [this](../bluebird/metrics/bluebird/config.py) config file.

## Vertical Separation

Name: `vertical_separation`

Description: Returns a value representing the vertical separation "score" between two aircraft.

Configuration parameters:
    - `VERT_LOS_SCORE` - Score below the minimum separation
    - `VERT_MIN_DIST` - Minimum distance 
    - `VERT_WARN_DIST` - Warning distance
    
Function: [vertical_separation(acid1, acid2)](../bluebird/metrics/bluebird/metrics.py)

Params: IDs of two aircraft which exist in the simulation

## Horizontal Separation

Name: `horizontal_separation`

Description: Returns a value representing the horizontal separation "score" between two aircraft.

Configuration parameters:
    - `HOR_LOS_SCORE` - Score below the minimum separation
    - `HOR_MIN_DIST` - Minimum distance 
    - `HOR_WARN_DIST` - Warning distance
    
Function: [horizontal_separation(acid1, acid2)](../bluebird/metrics/bluebird/metrics.py)

Params: IDs of two aircraft which exist in the simulation
