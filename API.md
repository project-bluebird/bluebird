
# BlueBird API

Version `1`

Notes:

- If sending a JSON body, the correct HTTP header must be sent: `Content-Type: application/json`.
- In future, this documentation will be auto-generated 😅
- Parameters should follow the [Docopt](http://docopt.org/) format
- Unless otherwise noted, all references to 'speed' refer to the aircraft airspeed (usually in CAS)
- In general, any endpoint may return a `400 Bad Request` if the required parameters were not provided in the correct format

## Contents

### Simulation endpoints

- [Define waypoint](#define-waypoint-defwpt)
- [Change Simulation Rate Multiplier](#change-simulation-rate-multiplier-dtmult)
- [Pause Simulation](#pause-simulation-hold)
- [Load Scenario](#load-scenario-ic)
- [Reload from Log](#load-log)
- [Resume Simulation](#resume-simulation-op)
- [Create Scenario](#create-scenario)
- [Reset Simulation](#reset-simulation)
- [Simulation Time](#simulation-time)
- [Simulation Step](#simulation-step-step)

### Aircraft endpoints

- [Add Waypoint](#add-waypoint-addwpt)
- [Altitude](#altitude)
- [Create Aircraft](#create-aircraft-cre)
- [Direct to Waypoint](#direct-to-waypoint-direct)
- [Heading](#heading)
- [List Route](#list-route-listroute)
- [Position](#position-pos)
- [Speed](#speed)
- [Vertical Speed](#vertical-speed)
- [Set Seed](#set-seed)

### Application endpoints

- [Episode Log](#episode-logfile)
- [Simulator Mode](#simulator-mode)
- [Shutdown](#shutdown)
- [Metrics](#metrics)
- [MetricProviders](#metric-providers)

---

## Define Waypoint (DEFWPT)

Defines a custom waypoint:

```javascript
POST /api/v1/defwpt
{
    "wpname": "TEST",
    "lat": 1.23,
    "lon": 4.56,
    ["type": "<type>"]
}
```

Notes:

- Currently BlueSky does not detect duplicate waypoints
- `<type>` is an (optional) custom string which can be used to tag waypoints

Returns:

- `201 Created` - Waypoint was defined
- `500 Internal Server Error` - Could not define the waypoint (error will be provided)

## Change Simulation Rate Multiplier (DTMULT)

Changes the simulation rate multiplier:

```javascript
POST /api/v1/dtmult
{
    "multiplier": 1.5
}
```

Returns:

- `200 Ok` - Rate multiplier was changed
- `400 Bad Request` - Rate multiplier was invalid
- `500 Internal Server Error` - Could not change the rate multiplier (error will be provided).

## Pause Simulation (HOLD)

Pauses the simulation:

```javascript
POST /api/v1/hold
```

Returns:

- `200 Ok` - Simulation was paused
- `500 Internal Server Error` - Simulation could not be paused

## Load Scenario (IC)

Resets the simulation and loads the scenario specified in the given filename. The `filename` parameter is required:

```javascript
POST /api/v1/ic
{
  "filename": "scenario/<scenario>.scn",
  ["multiplier": 1.0]   // Optional: simulation rate multiplier
}
```

Where the file path is relative to the BlueSky root directory. In future there will hopefully be some central store of scenario files which can be used in addition to the ones bundled with BlueSky.

Note that the `.scn` extension will always be added if not specified, so the scenarios `test` and `test.scn` are equivalent.

Returns:

- `200 Ok` - Scenario was loaded
- `400 Bad Request` - File extension or multiplier were invalid
- `500 Internal Server Error` - Could not load the scenario
	- This could be due to the file not existing, or case-sensitivity of the given filename (some are named `*.scn`, while others are `*.SCN`)

## Load Log

Reload the simulation to a particular time in an episode logfile:

```javascript
POST /api/v1/loadlog
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

Returns:

- `200 Ok` - Simulation was reloaded
- `400 Bad Request` - Invalid arguments or precondition. Response will contain more information
- `500 Internal Server Error` - Error performing the reload. Response will contain more information

## Resume Simulation (OP)

Resumes the simulation:

```javascript
POST /api/v1/op
```

Returns:

- `200 Ok` - Simulation was resumed
- `500 Internal Server Error` - Simulation could not be resumed

## Create Scenario

Creates a scenario with the provided content:

```javascript
POST /api/v1/scenario
{
    "scn_name": "test",
    "content": [
        "00:00:00>CRE SWR39W A320 EHAM RWY18L * 0 0",
        "00:00:01>SPD SWR39W 300",
        "00:00:01>ALT SWR39W FL300"
    ],
    ["start_new": true],    // Optional: start the simulation after upload
    ["start_dtmult": 5.0]   // Optional: simulation rate multiplier
}
```

Notes:

- The `.scn` extension will always be added if not specified, so the scenarios `test` and `test.scn` are equivalent.
- Any existing scenario with the same name will be overwritten
- Each line in `content` must contain a timestamp and a valid BlueSky command. The timestamp must be in the format `hh:mm:ss`
- A small delay should be included between creating an aircraft and issuing commands to it

Returns:

- `200 Ok` - Simulation was created and started
- `201 Created` - Simulation was created
- `400 Bad Request` - Error with simulation content
- `500 Internal Server Error` - Simulation could not be uploaded, or could not be started after upload

## Reset Simulation

Resets the simulation and clears all aircraft data:

```javascript
POST /api/v1/reset
```

Returns:

- `200 Ok` - Simulation was reset
- `500 Internal Server Error` - Simulation could not be reset

## Simulation Time

Get the current simulated time:

```javascript
GET /api/v1/time
```

Returns:

- `200 Ok` - Time retrieved. Data will of the form:

```javascript
{
    "sim_utc": "2019-04-17 00:12:08.300000"
}
```

- `500 Internal Server Error` - Time could not be retrieved - response will contain error info

## Simulation Step (STEP)

Step the simulation forward:

```javascript
POST /api/v1/step
```

Notes:

- The simulation must be in `agent` mode otherwise an error will be returned
- The timestep is based on `DTMULT`, so a setting of 5.0x will step forward 5 seconds

Returns:

- `200 Ok` - Simulation was stepped
- `400 Bad Request` - If the request was not made while in `agent` mode
- `500 Internal Server Error` - Could not step - response will contain error info

---

## Add Waypoint (ADDWPT)

Add a waypoint to the end of the aircraft's route:

```javascript
POST /api/v1/addwpt
{
    "acid": "SCN1001",
    ("wpname": "<waypoint>" | "lat": 123, "lon": 456),
    ["alt": "FL250"],
    ["spd": 250]
}
```

Notes:

- Either the `wpname`, or both a `lat` and `lon` must be provided

Returns:

- `200 Ok` - Command accepted
- `400 Bad Request` - Aircraft ID was invalid, or an accepted combination of arguments was not provided
- `404 Not Found` - Aircraft was not found in the simulation

## Altitude

This has both `POST` and `GET` versions.

`POST` - Request that the aircraft alters its altitude:

```javascript
POST /api/v1/alt
{
  "acid": <acid>,	// Aircraft ID
  "alt": "FL250",	// Requested altitude (feet or FL)
  ["vspd": "50"]	// Optional: vertical speed (ft/min)
}
```

Returns:

- `200 Ok` - Command accepted
- `400 Bad Request` - Aircraft ID was invalid
- `404 Not Found` - Aircraft was not found

`GET` - Get the current, requested, and cleared flight levels for an aircraft:

```javascript
GET /api/v1/alt?acid=<acid>
```

Notes:

- All returned flight levels are in meters
- The requested flight level can only be returned if the aircraft has a defined route
- The initial cleared flight level will be set to the initial altitude when the scenario is loaded

Returns:

- `200 Ok` - Data:

```javascript
{
    "fl_current": 7620,
    "fl_cleared": 4572,
    "fl_requested": 2896
}
```

- `400 Bad Request` - Aircraft ID was invalid, or does not exist in the simulation

## Create Aircraft (CRE)

Creates an aircraft. The following data must be provided:

```javascript
POST /api/v1/cre
{
  "acid": "TST1000",		// Aircraft ID (alphanumeric, at least 3 characters)
  "type": "B744",		// Aircraft type
  "lat": "0",			// Initial latitude (deg)
  "lon": "0",			// Initial longitude (deg)
  "hdg": "0",			// Initial heading (deg)
  "alt": "FL250",		// Initial altitude (feet or FL)
  "spd": "250"			// Initial calibrated air speed (CAS) (kts or Mach)
}
```

Returns:

- `201 Created` - Aircraft was created
- `400 Bad Request` - Aircraft already exists
- `500 Internal Server Error` - Other error, response will contain data e.g.:

```javascript
"Error: simulation returned: Syntax error processing argument 5:"
"Could not parse \"-FL050\" as altitude"
"CRE acid,type,lat,lon,hdg,alt,spd"
```

## Direct to Waypoint (DIRECT)

Instructs an aircraft to go directly to the specified waypoint. The waypoint must exist on the aircraft's route.

```javascript
POST /api/v1/direct
{
    "acid": "TST1000",      // Aircraft ID (alphanumeric, at least 3 characters)
    "waypoint": "TESTWPT"   // The name of the waypoint to go to
}
```

Returns:

- `200 Ok` - Command was excepted
- `400 Bad Request` - Aircraft ID was invalid
- `404 Not Found` - The specified aircraft did not exist in the simulation
- `500 Internal Server Error` - Other error, response will contain data. Note there is currently no way to distinguish between the waypoint not existing, and the waypoint extsting but not being on the aircraft's route.

## Heading

Request that the aircraft changes its heading:

```javascript
POST /api/v1/hdg
{
  "acid": <acid>,	// Aircraft ID
  "hdg": "123.45"	// Requested heading (deg)
}
```

Returns:

- `200 Ok` - Command accepted
- `400 Bad Request` - Aircraft ID was invalid
- `404 Not Found` - Aircraft was not found

## List Route (LISTROUTE)

Returns a list of the waypoints on an aircraft's route:

```javascript
GET /api/v1/listroute?acid=<acid>
```

Returns:

- `200 Ok` - Returns the following data:

```javascript
{
    "acid": "SCN1001",
    "route": [
        {
            "is_current": true,
            "req_alt": "FL250",
            "req_spd": 123,
            "wpt_name": "BKN"
        },
        {
            "is_current": false,
            "req_alt": "4500",
            "req_spd": 100,
            "wpt_name": "SPY"
        }
    ],
    "sim_t": 1234
}
```

- `400 Bad Request` - Aircraft ID was invalid,
- `404 Not Found` - Aircraft does not exist in the simulation.
- `500 Internal Server Error` - Other error i.e. route data could not be parsed, or the specified aircraft has no route (response will contain data).

## Position (POS)

Request information on specific aircraft, or all:

```javascript
GET /api/v1/pos?acid=[<acid>[,<acid> ...]|"all"]
```

Returns:

- `200 Ok` - Returns the following data:

```javascript
{
  "SCN1001": {				// The requested acid (aircraft ID)
    "actype": "B747"        		// Aircraft type
    "alt": 6096,			// Altitude (m)
    "gs": 293.6780042365748,		// Ground speed (m/s)
    "lat": 53.8,			// Latitude (deg)
    "lon": 2.0364214816067467,		// Longitude (deg)
    "vs": 0				// Vertical speed (ft/min)
  },
  "sim_t": 123                  	// Sim time (seconds since start of scenario)
}
```

- `400 Bad Request` - Aircraft ID was invalid, or no aircraft exist (when `?acid=ALL` specified)
- `404 Not Found` - Aircraft was not found. It may have been removed after travelling outside an experiment area.

## Speed

Request that the aircraft changes its speed:

```javascript
POST /api/v1/spd
{
  "acid": <acid>,	// Aircraft ID
  "spd": "250"		// Requested calibrated air speed (CAS) (kts or Mach)
}
```

Returns:

- `200 Ok` - Command accepted
- `400 Bad Request` - Aircraft ID was invalid
- `404 Not Found` - Aircraft was not found

## Vertical Speed

Request that the aircraft changes its vertical speed:

```javascript
POST /api/v1/vs
{
  "acid": <acid>,	// Aircraft ID
  "vspd": "250"		// Requested vertical speed (ft/min)
}
```

Returns:

- `200 Ok` - Command accepted
- `400 Bad Request` - Aircraft ID was invalid
- `404 Not Found` - Aircraft was not found

## Set Seed

Sets the random seed of the simulator. Must be an unsigned 32-bit integer:

```javascript
POST /api/v1/seed
{
    "value": 1234
}
```

Returns:

- `200 Ok` - Seed was set
- `400 Bad Request` - Invalid seed provided
- `500 Internal Server Error` - Other error when setting seed (response will contain data)

---

## Episode Logfile

Returns the content of the current episode's logfile:

```javascript
GET /api/v1/eplog[?close_ep]
```

The `close_ep` parameter can be used to close the episode and reset the simulator.

Returns:

- `200 Ok` - Returns the following data:

```javascript
{
  "cur_ep_file": <full path to episode log file>,
  "cur_ep_id": <episode id>,
  "lines": [...]
}
```

Where the `lines` array contains each line from the log file.

- `404 Not Found` - No episode is being recorded

## Simulator Mode

Change the current simulator mode:

```javascript
POST /api/v1/simmode
{
    "mode": "agent"
}
```

Notes:

- Currently available modes are `sandbox` and `agent`
- This affects any currently running simulation:
    - Setting `agent` mode will pause the current simulation and the episode log
    - Setting `sandbox` mode will resume the simulation and logging at the previous rate

Returns:

- `200 Ok` - Mode was updated
- `400 Bad Request` - Invalid mode specified
- `500 Internal Server Error` - Other error when changing mode (response will contain data)

## Shutdown

Shuts down the BlueBird server:

```javascript
POST /api/v1/shutdown
```

Returns:

- `200 Ok` - Server is shutting down
- `500 Internal Server Error` - Could not shutdown. Error data will be provided.

## Metrics

Calls a metric function. E.g.:

```javascript
GET /api/v1/metric?name=vertical_separation&args=SCN1001,SCN1002
```

Notes:

- A full list of the included metrics in BlueBird is [here](docs/Metrics.md)

Returns:

- `200 Ok` - Result of the metric function:

```javascript
{
    "vertical_separation": -1
}
```

- `400 Bad Request` - Invalid arguments for the specified metric function, or the arguments were invalid. E.g. "Expected the aircraft to exist in the simulation"
- `404 Not Found` - No metric found with the given name
- `500 Internal Server Error` - No metrics available

## Metric Providers

Get a list of the available metric providers:

```javascript
GET /api/v1/metricproviders
```

Returns:

- `200 Ok` - Dictionary of the available providers, and their versions:
```javascript
{
    "BlueBirdProvider": "1.3.0-dev"
}
```
