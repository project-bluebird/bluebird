
# BlueBird

Server to communicate with NATS air traffic simulator and BlueSky

## Initial Prototype

See [here](docs/InitialProto.md).

## Usage

### Running

Using docker, run BlueSky and BlueBird with the provided script:

```bash
> ./run-docker.sh
```

Can also run locally if you have a BlueSky simulation running:

```bash
> ./install.sh
> python ./run.py # Can also pass --bluesky_host=1.2.3.4 if you have BlueSky running somewhere else
```

### Commands

Currently available commands are `IC`, `POS`, and `CRE`. Example:

- `GET` `localhost:5001/api/v1/pos/<acid/all>` - Get POS info on aircraft `<acid>`, or for `<all>`

- `POST` `localhost:5001/api/v1/ic` - Reset the sim to the start of a scenario. If not passed any data, will reset the current scenario. Can also pass the following JSON to load a file (path relative to the BlueSky sim):
```json
{
  "filename": "scenario/8.SCN"
}
```

- `POST` `localhost:5001/api/v1/cre` - Create an aircraft. Must provide the following JSON body:
```json
{
  "acid": "test1234",
  "type": "B744",
  "lat": "0",
  "lon": "0",
  "hdg": "0",
  "alt": "FL250",
  "spd": "250"
}
```

Note: If sending a JSON body, the following HTTP header must be sent: `Content-Type: application/json`

## Development

Pylint can be run with the included rc file:

```bash
> pylint --rcfile .pylintrc bluebird # Can also pass paths to individual modules or packages
```