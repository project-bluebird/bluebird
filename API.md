
# BlueBird API

Version `2`

Notes:

- If sending JSON data, the correct HTTP header must be sent: `Content-Type: application/json`.
- The request parameters defined below should follow the [Docopt](http://docopt.org/)
format
- Unless otherwise stated, each endpoint can return the following set of responses:
  - `200 Ok` - The request was accepted
  - `400 Bad Request` - Invalid or missing arguments
  - `500 Internal Server Error` - An error was encountered when processing the request.
  This can occur if the simulator rejects the command for some reason. An error message
  will usually be provided.
- Altitudes can be specified in 2 formats:
  - [Flight level](https://en.wikipedia.org/wiki/Flight_level) as a string, e.g. `"FL150"`
  - Feet as an integer, e.g. `15000`

## Contents

### Simulation endpoints

- [Set Speed Multiplier](#set-speed-multiplier)
- [Pause Simulation](#pause-simulation)
- [Reload from Log](#load-log)
- [Resume Simulation](#resume-simulation)
- [Reset Simulation](#reset-simulation)
- [Scenario](#scenario)
- [Sector](#sector)
- [Set Seed](#set-seed)
- [Simulation Step](#simulation-step)

### Aircraft endpoints

- [Altitude](#altitude)
- [Create Aircraft](#create-aircraft)
- [Direct to Waypoint](#direct-to-waypoint)
- [Heading](#heading)
- [List Route](#list-route)
- [Position](#position)
- [Speed](#ground-speed)

### Application endpoints

- [Episode Info](#episode-info)
- [Episode Log](#episode-logfile)
- [Simulation Info](#simulation-info)
- [Shutdown](#shutdown)

### Metrics endpoints

- [Metrics](#metrics)
- [MetricProviders](#metric-providers)

---

## Set speed multiplier

- [Definition](bluebird/api/resources/dtmult.py)

Changes the simulation speed multiplier. In agent mode, this corresponds to the number
of seconds which are progressed during a `STEP` command.

```javascript
POST /api/v2/dtmult
{
    "multiplier": 1.5
}
```

## Pause Simulation

- [Definition](bluebird/api/resources/hold.py)

Pauses the simulation. Only valid when in sandbox mode.

```javascript
POST /api/v2/hold
```

## Load Log

_Currently disabled_

- [Definition](bluebird/api/resources/loadlog.py)

Reload the simulation to a particular point in time from the provided episode log file:

```javascript
POST /api/v2/loadlog
{
    ("filename": "/path/to/file.log" |
    "lines": ["line1", "line2", ...]),
    "time": 60
}
```

Notes:

- Either `filename` or `lines` must be specified
- `filename` must be relative to BlueBird's root directory
- This API can only be used in agent mode
- Only logfiles which have had their random seed set can be loaded

## Resume Simulation

- [Definition](bluebird/api/resources/op.py)

Resumes the simulation:

```javascript
POST /api/v2/op
```

## Reset Simulation

- [Definition](bluebird/api/resources/reset.py)

Resets the simulation and clears all aircraft data:

```javascript
POST /api/v2/reset
```

## Scenario

- [Definition](bluebird/api/resources/scenario.py)

Upload a new scenario definition, or load an existing definition. The scenario data
format is defined by [Aviary](https://github.com/alan-turing-institute/aviary/blob/master/README.md).

```javascript
POST /api/v2/scenario
{
    "name": "scenario-test",
    ["content": {...}]
}
```

Notes:

- Any existing scenario with the same name will be overwritten
- This endpoint requires that a sector definition has already been uploaded

Returns:

- `201 Created` - Scenario was loaded

## Sector

- [Definition](bluebird/api/resources/sector.py)

### `GET`

Get the current sector definition.

```javascript
GET /api/v2/sector
```

A valid response looks like:

```javascript
{
    "name": "test-sector",
    "content": {...}        // Sector GeoJSON
}
```

### `POST`

Upload a new sector definition, or load an existing definition. The sector data format
is defined by [Aviary](https://github.com/alan-turing-institute/aviary/blob/master/README.md).

```javascript
POST /api/v2/sector
{
    "name": "sector-test",
    ["content": {...}]      // Sector GeoJSON
}
```

Notes:

- Any existing sector with the same name will be overwritten

Returns:

- `201 Created` - Scenario was loaded

## Seed

- [Definition](bluebird/api/resources/seed.py)

Sets the random seed of the simulator. Must be an unsigned 32-bit integer:

```javascript
POST /api/v2/seed
{
    "value": 1234
}
```

## Simulation Step

- [Definition](bluebird/api/resources/step.py)

Step the simulation forward. Only valid when in agent mode.

```javascript
POST /api/v2/step
```

Notes:

- The step is based on the `DTMULT` value, so a setting of 5.0x will step forward 5
seconds

---

## Altitude

- [Definition](bluebird/api/resources/alt.py)

Request that the aircraft alters its altitude:

```javascript
POST /api/v2/alt
{
  "callsign": "AC1001",
  "alt": "FL250",
  ["vspd": "50"]
}
```

## Create Aircraft

- [Definition](bluebird/api/resources/cre.py)

Creates an aircraft.

```javascript
POST /api/v2/cre
{
  "callsign": "TST1000",
  "type": "B744",
  "lat": "0",
  "lon": "0",
  "hdg": "0",
  "alt": "FL250",
  "gspd": "250"
}
```

Returns:

- `201 Created` - Aircraft was created

## Direct to Waypoint

- [Definition](bluebird/api/resources/direct.py)

Instructs an aircraft to go directly to the specified waypoint. The waypoint must exist
on the aircraft's route.

```javascript
POST /api/v2/direct
{
    "callsign": "TST1000",
    "waypoint": "FRED"
}
```

## Heading

- [Definition](bluebird/api/resources/hdg.py)

Request that the aircraft changes its heading:

```javascript
POST /api/v2/hdg
{
  "callsign": "AC1001",
  "hdg": "123.45"
}
```

## List Route

- [Definition](bluebird/api/resources/listroute.py)

Returns a list of the waypoints on an aircraft's route:

```javascript
GET /api/v2/listroute?callsign=AC1001
```

A valid response looks like:

```javascript
{
    "callsign": "AC1001",
    "route": [
        {
            "is_current": true,
            "req_alt": "FL250",
            "req_gspd": 123,
            "wpt_name": "BKN"
        },
        {
            "is_current": false,
            "req_alt": "4500",
            "req_gspd": 100,
            "wpt_name": "SPY"
        }
    ]
}
```

## Position

- [Definition](bluebird/api/resources/pos.py)

Request information on specific aircraft, or all:

```javascript
GET /api/v2/pos[?callsign=AC1001]
```

A valid response looks like:

```javascript
{
  "AC1001": {
    "actype": "B747"
    "cleared_fl": 22500,
    "current_fl": 20000,
    "gs": 293.6,
    "hdg": 120.4,
    "lat": 53.8,
    "lon": 2.036421,
    "requested_fl": 25000,
    "vs": 0
  },
  "scenario_time": 123
}
```

Notes (check both of these):

- The requested flight level can only be returned if the aircraft has a defined route
- The initial cleared flight level will be set to the initial altitude when the scenario is loaded

## Ground Speed

- [Definition](bluebird/api/resources/gspd.py)

Request that the aircraft changes its ground speed:

```javascript
POST /api/v2/gspd
{
  "callsign": "AC1001",
  "gspd": 250
}
```

---

## Episode Info

- [Definition](bluebird/api/resources/epinfo.py)

Returns the current episode information. Only valid in agent mode.

```javascript
GET /api/v2/epinfo
```

A valid response looks like:

```javascript
{
    "inst_id": "108f16ee-3542-11ea-9b2c-c8f7501b2c7e",
    "cur_ep_id": "a30b445f-a598-4594-a794-7a73e5587b9f",
    "cur_ep_file": "path/to/logfile.log",
    "log_dir": "path/to/log/dir",
}
```

## Episode Logfile

- [Definition](bluebird/api/resources/eplog.py)

Returns the content of the current episode's logfile. Only valid in agent mode.

```javascript
GET /api/v2/eplog[?close_ep]
```

Notes:

- The `close_ep` parameter can be used to close the episode and reset the simulator.

A valid response looks like:

```javascript
{
  "cur_ep_file": "path/to/episode/file.log",
  "cur_ep_id": "a30b445f-a598-4594-a794-7a73e5587b9f",
  "log": [...]
}
```

## Sim Info

- [Definition](bluebird/api/resources/siminfo.py)

Returns the current simulation info.

```javascript
GET /api/v2/siminfo
```

A valid response looks like:

```javascript
{
    "callsigns": ["AC1001", "AC1002", ...],
    "mode": "Agent",
    "sector_name": "test-sector",
    "scenario_name": "test-scenario",
    "scenario_time": 123,
    "seed": 0,
    "sim_type": "BlueSky",
    "speed": 0.0,
    "state": "HOLD",
    "dt": 0.01,
    "utc_datetime": "2020-01-12 13:59:18.467786"
}
```

## Shutdown

- [Definition](bluebird/api/resources/shutdown.py)

Shuts down the BlueBird server:

```javascript
POST /api/v2/shutdown[?stop_sim]
```

Notes:

- If `stop_sim` is requested, then BlueBird will also attempt to stop the simulation
server

---

## Metric

Returns the value of the requested metric.

```javascript
GET /api/v2/metric?name=pairwise_separation&args=AC1001,AC1002
```

Notes:

- A full list of the included metrics in BlueBird is [here](docs/metrics.md)

A valid response (for the example metric) looks like:

```javascript
{
    "pairwise_separation": -1
}
```

## Metric Providers

Get a list of the available metric providers.

```javascript
GET /api/v2/metricproviders
```

An example response looks like:

```javascript
{
    "BlueBird": "1.3.0-dev"
}
```
