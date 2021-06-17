
[![Build Status](https://travis-ci.com/alan-turing-institute/bluebird.svg?branch=master)](https://travis-ci.com/alan-turing-institute/bluebird)
![Python Version](https://img.shields.io/badge/python-3.7-blue)
![License](https://img.shields.io/github/license/alan-turing-institute/bluebird)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

Active develoment moved under [Project BlueBird](https://github.com/project-bluebird).

# BlueBird

BlueBird provides a common [Flask](https://github.com/pallets/flask)-based API to multiple air traffic simulators. In addition to basic communication, it also includes features such as state caching, performance metrics (via [Aviary](https://github.com/alan-turing-institute/aviary)), and logging of scenario data. The main purpose of BlueBird is to provide a common interface to ease the research & development of AI for air traffic control.

The currently supported open-source simulator is [BlueSky](https://github.com/alan-turing-institute/bluesky).

## Usage

### Running locally

To run locally, first start a supported simulation server, then:

```bash
$ ./install.sh [--dev] [<venv_name>]
$ source <venv_name>/bin/activate
(venv) > python ./run.py [--sim-host=<address>] [--sim-mode=<mode>] [--reset-sim] [--log-rate=<rate>]
```

Notes:

- the `--dev` option will also install dependencies needed for developing BlueBird
- If you need to connect to BlueSky on another host (i.e. on a VM), you may pass the `--sim-host` option to run.py.
- If passed, `--reset-sim` will reset the simulation on connection
- If passed, `--sim-mode` will start the simulation in a specific [mode](docs/SimulatorModes.md).

### Running with Docker

BlueBird can also be run through Docker. Easiest way is to run with docker-compose:

```bash
$ docker-compose up -d
```

This will also pull and start a BlueSky simulator container.

You can also use the pre-built `turinginst/bluebird` image, or build it yourself. This uses `localhost` for the BlueSky host. This can be overridden with environment variable:

```bash
$ docker run --rm -e BS_HOST="1.2.3.4" turinginst/bluebird:latest
```

### API Endpoints

See [here](API.md).

### Logging

By default, BlueBird creates two log files:

- `logs/<timestamp>-<instance_id>/debug.log` Contains general application logging and Flask request info. One file per instance of BlueBird. The `instance_id` is a unique identifier based on the ID of the host machine and the current time.
- `logs/<timestamp>-<instance_id>/<timestamp>-<episode_id>.log` Contains a log of aircraft and simulation data. A new file is created for each scenario that is loaded, and the file is closed if the simulation is reset. The `episode_id` is a random unique identifier.
    - Entries prefixed with 'A' contain info on the aircraft in the simulation
    - Entries prefixed with 'E' contain info on episode events (start/end, file loaded)
    - Entries prefixed with 'C' contain info on commands sent to the simulator

The episode file is only recorded for Agent mode.

The timestamps of the `logs/*` directories are the start times of the BlueBird app, whereas the timestamps in the episode file names are the start of each episode.

## Development

### Installation

To install development packages, pass the `--dev` option to the install script. Or if you have already created a virtual environment:

```bash
$ pip install -r requirements-dev.txt
$ pre-commit install
```

### Testing

The unit test suite can be run with:

```bash
$ pytest [<optional-arguments>] tests
```

You can also pass paths to individual modules or tests:

```bash
$ pytest [<optional-arguments>] <test-file>::<test-name>
```

Integration tests can run with each supported simulator, however they will only be run in a CI environment unless forced with the `--run-integration` flag.

Integration tests require Docker to run. To specify a different docker daemon host than localhost, you can pass `--docker-host=<host address>:<port>`. This can be useful when testing if you don't have Docker locally installed, or if the images required for testing are only available on a remote host.

The default integration simulator is BlueSky. To test against a different simulator, specify it with the `--integration-sim=<sim name>` option.

### Code Quality

BlueBird uses [pre-commit] to help ensure code quality and correctness. Once installed, this automatically runs as part of the git commit process.

---

[pre-commit]: https://pre-commit.com
