
# BlueBird API Endpoints

Note: If sending a JSON body, the correct HTTP header must be sent: `Content-Type: application/json`.

- `POST <host>/api/v1/ic`

Reset the simulation to the start of a scenario. If not passed any data, the currently running scenario will be reset (if one is running). A scenario file can also be loaded by sending the following data to the endpoint:

```json
{
  "filename": "scenario/8.SCN"
}
```

Where the file path is relative to the BlueSky root directory.

Returns:

TODO

- `POST <host>/api/v1/cre`

Create an aircraft. The following data must be provided:

TODO List of valid aircraft types (as an endpoint?)

```json
{
  "acid": <acid>,
  "type": "B744",
  "lat": "0",
  "lon": "0",
  "hdg": "0",
  "alt": "FL250",
  "spd": "250"
}
```

Returns:

TODO

- `GET <host>/api/v1/pos`

Request the information for a specific aircraft by sending its aircraft ID (`acid`), or all aircraft in the current simulation:

```json
{
  "acid": (<acid>|"ALL")
}
```

Returns:

```json
{
  "SCN1001": {
    "_validTo": "Thu, 24 Jan 2019 13:53:48 GMT",
    "alt": 6096,
    "gs": 293.6780042365748,
    "lat": 53.8,
    "lon": 2.0364214816067467,
    "vs": 0
  },
  // ...
}
```

- `POST <host>/api/v1/alt`

Request that the aircraft alters its altitude:

```json
{
  "acid": <acid>,
  "alt": "FL250"
}
```

Can also optionally pass the vertical speed at which to climb or descend at:

```json
{
  "acid": <acid>,
  "alt": "FL250",
  "vspd": 50
}
```

Returns:

TODO