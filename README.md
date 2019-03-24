
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
> source <venv_name>/bin/activate
(venv) > python ./run.py [--bluesky_host=<address>] [--reset_sim] [--log_rate=<rate>]
```

Notes:
- the `--dev` option will also install dependencies needed for developing BlueBird
- If you need to connect to BlueSky on another host (i.e. on a VM), you may pass the `--bluesky_host` option to run.py.
- If passed, `--reset_sim` will reset the simulation on connection

### Running with Docker

BlueBird can also be run through Docker. Easiest way is to run the provided script:

```bash
> ./run-docker.sh
```

This first creates a BlueSky image using the git sub-module, then composes a pair of BlueSky/BlueBird containers with the appropriate networking and runs them (see [docker-compose.yml](docker-compose.yml)).

### API Endpoints

See [here](API.md).

### Logging

By default, BlueBird creates two log files:

- `logs/<timestamp>-debug.log` Contains general application logging, Flask request info
- `logs/<timestamp>-episode.log` Contains a log of aircraft and simulation data. A new file is created for each scenario that is loaded, and the file is closed if the simulation is reset
    - Entries prefixed with 'A' contain info on the aircraft in the simulation
    - Entries prefixed with 'E' contain info on episode events (start/end, file loaded)
    - Entries prefixed with 'C' contain info on commands sent to the simulator

The rate at which aircraft data is logged to the episode files is configurable with the `SIM_LOG_RATE` variable in the settings. This value represents the frequency of logging in terms of the simulator time. This can be set at startup with the `--log_rate` option.

## Development

### Installation

To install development packages, pass the `--dev` option to the install script. Or if you have already created a virtual environment:

```bash
> pip install -r requirements-dev.txt
```

### Testing

The unit test suite can be run with:

```bash
> pytest [<optional-arguments>] ./tests/unit
```

You can also pass paths to individual modules or tests:

```bash
> pytest [<optional-arguments>] ./tests/unit/test_api_commands.py::test_pos_command
```

TODO: Integration tests using BlueSky

### Code Style

Linting can be run with the included `.pylintrc` file:

```bash
> pylint --rcfile=.pylintrc [--enable=<msg>] ./bluebird
```

The .pylintrc contains some useful configuration for linting. Specific warnings can be re-enabled with the `--enable` option. E.g. to view all TODO notes (which are disabled in our config), use `--enable=fixme`.

You can also pass paths to individual modules or packages. If using pylint as part of a bash script, then you may wish to use [pylint-exit](https://github.com/jongracecox/pylint-exit) to interpret the exit code correctly. Usage example:

```bash
pylint [<optional-arguments>] ./bluebird || pylint-exit $?
if [ $? -ne 0 ]; then
  echo "An error occurred while running pylint." >&2
  exit 1
fi
```
