  
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
- [Simulation Speed Change](#simulation-speed-change-dtmult)
- [Simulation Pause](#simulation-pause-hold)
- [Scenario Load](#scenario-load-ic)
- [Simulation Resume](#simulation-resume-op)
- [Simulation Reset](#simulation-reset)
- [Simulation Time](#simulation-time-time)

### Aircraft endpoints

- [Add Waypoint](#add-waypoint-addwpt)
- [Altitude](#altitude)
- [Create Aircraft](#create-aircraft-cre)
- [Direct to Waypoint](#direct-to-waypoint-direct)
- [Heading](#heading)
- [List Route](#list-route-listroute)
- [Position](#position)
- [Speed](#speed)
- [Vertical Speed](#vertical-speed)

### Application endpoints

- [Episode Info](#episode-info)

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
- `500 Internal Server Error` - Could not change the speed (error will be provided)

## Simulation Speed Change (DTMULT)

Changes the simulation speed:

```javascript
POST /api/v1/dtmult
{
    "multiplier": 1.5
}
```

Returns:

- `200 Ok` - Speed was changed
- `400 Bad Request` - Multiplier was invalid
- `500 Internal Server Error` - Could not change the speed (error will be provided).

## Simulation Pause (HOLD)

Pauses the simulation:

```javascript
POST /api/v1/hold
```

Returns:  

- `200 Ok` - Simulation was paused
- `500 Internal Server Error` - Simulation could not be paused

## Scenario Load (IC)

Resets the simulation and loads the scenario specified in the given filename. The `filename` parameter is required:

```javascript
POST /api/v1/ic
{
  "filename": "scenario/<scenario>.scn",
  ["multiplier": 1.0]   // Optional: speed multiplier
}
```  
 
Where the file path is relative to the BlueSky root directory. The filename must end with `.scn`. In future there will hopefully be some central store of scenario files which can be used in addition to the ones bundled with BlueSky.

Returns:

- `200 Ok` - Scenario was loaded
- `400 Bad Request` - File extension or multiplier were invalid
- `500 Internal Server Error` - Could not load the scenario
	- This could be due to the file not existing, or case-sensitivity of the given filename (some are named `*.scn`, while others are `*.SCN`)

## Simulation Resume (OP)

Resumes the simulation:

```javascript
POST /api/v1/op
```

Returns:  

- `200 Ok` - Simulation was resumed
- `500 Internal Server Error` - Simulation could not be resumed

## Simulation Reset

Resets the simulation and clears all aircraft data:

```javascript
POST /api/v1/reset
```

Returns:  

- `200 Ok` - Simulation was reset
- `500 Internal Server Error` - Simulation could not be reset

## Simulation Time

Get or set the current simulated time:

```javascript
POST /api/v1/time
{
    ["time": <time>]
}
```

The `<time>` argument (if specified) must be one of the following:

- `RUN` - Default if not specified. Returns the current simulated time
- `REAL` - Return the current UTC time (not sure this is particularly useful...)
- `HH:MM:SS.mmm` - Set the simulated time to the given time-string

Returns:  

- `200 Ok` - Simulation time was set
- `500 Internal Server Error` - Time could not be set, or input time was invalid

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
  
Request that the aircraft alters its altitude:

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
    ]    
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
    "alt": 6096,			// Altitude (ft)
    "gs": 293.6780042365748,		// Ground speed (kts)
    "lat": 53.8,			// Latitude (deg)
    "lon": 2.0364214816067467,		// Longitude (deg)    
    "vs": 0				// Vertical speed (ft/min)
  },
  "sim_t": 123                  	// Sim time (seconds since start of scenario)
}  
```  

- `400 Bad Request` - Aircraft ID was invalid, or no aircraft exist (when `?acid=ALL` specified)
- `404 Not Found` - Aircraft was not found

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

---

## Episode Info

Returns information for the current episode

```javascript
GET /api/v1/epinfo  
```

Returns:

- `200 Ok` - Returns the following data:

```javascript
{
  "cur_ep_file": <full path to episode log file>,
  "cur_ep_id": <episode id>,
  "inst_id": <application instance id>,
  "log_dir": <application log directory>
}  
```  
