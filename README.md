
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
(venv) > python ./run.py [--bluesky_host=<address>]
```

Note: If you need to connect to BlueSky on another host (i.e. on a VM), you may pass the `--bluesky_host` option to run.py.

### Running with Docker

BlueBird can also be run through Docker. Easiest way is to run the provided script:

```bash
> ./run-docker.sh
```

This first creates a BlueSky image using the git sub-module, then composes a pair of BlueSky/BlueBird containers with the appropriate networking and runs them (see [docker-compose.yml](docker-compose.yml)).

### API Endpoints

See [here](API.md).


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
> pylint --rcfile .pylintrc ./bluebird
```

You can also pass paths to individual modules or packages. If using pylint as part of a bash script, then you may wish to use [pylint-exit](https://github.com/jongracecox/pylint-exit) to interpret the exit code correctly. Usage example:

```bash
pylint [<optional-arguments>] ./bluebird || pylint-exit $?
if [ $? -ne 0 ]; then
  echo "An error occurred while running pylint." >&2
  exit 1
fi
```
