  
# BlueBird API

Version `1`

Notes:

- If sending a JSON body, the correct HTTP header must be sent: `Content-Type: application/json`.  
- In future, this documentation will be auto-generated 😅
- Parameters should follow the [Docopt](http://docopt.org/) format
- Unless otherwise noted, all references to 'speed' refer to the aircraft airspeed (usually in CAS)

## Contents

### Simulation endpoints

- [Scenario Load](#scenario-load-ic)
- [Simulation Reset](#simulation-reset)
- [Simulation Pause](#simulation-pause-hold)
- [Simulation Resume](#simulation-resume-op)

### Aircraft endpoints

- [Create Aircraft](#create-aircraft-cre)
- [Position](#position)
- [Altitude](#altitude)
- [Heading](#heading)
- [Speed](#speed)
- [Vertical Speed](#vertical-speed)

## Scenario Load (IC)

Resets the simulation and loads the scenario specified in the given filename. The `filename` parameter is required:

```javascript
POST /api/v1/ic
{
  "filename": "scenario/<scenario>.scn"
}
```  
 
Where the file path is relative to the BlueSky root directory. The filename must end with `.scn`. In future there will hopefully be some central store of scenario files which can be used in addition to the ones bundled with BlueSky.

Returns:

- `200 Ok` - Scenario was loaded
- `400 Bad Request` - Filename was invalid
- `500 Internal Server Error` - Could not load the scenario
	- This could be due to the file not existing, or case-sensitivity of the given filename (some are named `*.scn`, while others are `*.SCN`)
  
## Simulation Reset

Resets the simulation and clears all aircraft data:

```javascript
POST /api/v1/reset
```

Returns:  

- `200 Ok` - Simulation was reset
- `500 Internal Server Error` - Simulation could not be reset

## Simulation Pause (HOLD)

Pauses the simulation:

```javascript
POST /api/v1/hold
```

Returns:  

- `200 Ok` - Simulation was paused
- `500 Internal Server Error` - Simulation could not be paused

## Simulation Resume (OP)

Resumes the simulation:

```javascript
POST /api/v1/op
```

Returns:  

- `200 Ok` - Simulation was resumed
- `500 Internal Server Error` - Simulation could not be resumed

---

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
- `500 Internal Server Error` - Other error, response will contain data:
 
```javascript
{TODO}
```
  
## Position

Request information on one or all aircraft

```javascript
GET /api/v1/pos?acid=[<acid>|"all"]
```
  
Returns:

- `200 Ok` - Returns the following data:

```javascript
{
  "SCN1001": {						// The requested acid (aircraft ID)
    "_validTo": "Thu, 24 Jan 2019 13:53:48 GMT",	// Estimate of when the data should be considered accurate to
    "alt": 6096,					// Altitude (ft)
    "gs": 293.6780042365748,				// Ground speed (kts)
    "lat": 53.8,					// Latitude (deg)
    "lon": 2.0364214816067467,				// Longitude (deg)
    "vs": 0						// Vertical speed (ft/min)
  },
  // ...
}  
```  

- `400 Bad Request` - Aircraft ID was invalid
- `404 Not Found` - Aircraft was not found

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
