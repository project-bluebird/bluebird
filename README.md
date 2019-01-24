
# BlueBird

BlueBird is a web API for air traffic simulators.

Currently supports:

- [BlueSky](https://github.com/alan-turing-institute/bluesky)

Future:

- NATS Machine College 😊


## Initial Prototype

See [here](docs/InitialProto.md).


## Usage

### Running locally

To run locally, first start a BlueSky simulation, then:

```bash
> ./install.sh [--dev] [<venv_name>]
> python ./run.py [--bluesky_host=<address>]
```

Note: If you need to connect to BlueSky on another host (i.e. on a VM), you may pass the `--bluesky_host` option to run.py.

### Running with Docker

BlueBird can also be run through Docker. Easiest way is to run the provided script:

```bash
> ./run-docker.sh
```

This first creates a BlueSky image using the git submodule, then composes a pair of BlueSky/BlueBird containers with the appropriate networking and runs them (see `docker-compose.yml`).

### Commands

- `GET /api/v1/pos`



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