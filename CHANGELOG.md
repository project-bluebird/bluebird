
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

-   Added support for loading the config settings from a file
-   Tidy-up handling of echo messages from BlueSky
-   Make the step command a bit more robust to timeouts for BlueSky. Uses the BS_TIMEOUT setting

## [2.0.2] - 2020-05-26

## Changed

- Print BlueBird version on startup to help debugging
- Ran pre-commit autoupdate and applied changes from pyupgrade and flake8
- Improve error message returned when BlueSky submodule not initialised
- Return a more useful 404 message if the wrong API version is specified

## [2.0.1] - 2020-05-08

### Fixed

- Fixed bug in parsing of altitudes from scenario JSON

### Changed

- Increase BlueSky stream timeout to 5s (#93)

## [2.0.0] - 2020-04-26

NOTE: This is a major rewrite of the application

### Added

- Added support for the MachColl simulator
- Added support for uploading scenario and sector definitions
- Added metrics endpoints
- Require BlueSky at v1.4.1 or greater
- Added [Aviary](https://github.com/alan-turing-institute/aviary)
- Added [black](https://black.readthedocs.io/en/stable/index.html) formatter to requirements and CI script
- Added datacalsses to simplify handling of physical units
- Added pre-commit

### Changed

- Changes to the API can be found [here](docs/api-v2-changes.md)
- Python 3.7+ is now required
- Changed `indent-string` from tabs to 4 spaces in `.pylintrc`
- Replaced underscores with dashes in all of the CLI options

## [1.3.0] - 2019-09-24

### Added

- BlueBird simulator [modes](docs/SimulatorModes.md)
- `STEP` endpoint to manually step the simulation forwards when in agent mode
- `SIMMODE` endpoint to allow switching between modes at runtime
- `SEED` endpoint to allow setting BlueSky's random seed
- `LOADLOG` endpoint to reset the sim to a given point from a logfile
- Added basic aircraft separation metric
- Added `GET` option to the `ALT` endpoint, to return the 3 versions of the flight levels

### Changed

- Bump required BlueSky version to `1.2.1`
- When in `agent` mode, aircraft data is only logged after each `STEP` command
- Point BlueSky submodule at `tags/turing-1.2.1`
- Scenarios containing no aircraft are now treated as invalid

### Removed

- Removed static page which rendered and served the README markdown file
- Removed the markdown pip dependency


## [1.2.1] - 2019-06-11

### Changed

- Include default BlueSky scenarios in the Docker image build
- Remove extra `\n` at end of episode log lines (`EPLOG` endpoint)

### Fixed

- Fix docker compose file for running integration tests on Windows
- [#62](https://github.com/alan-turing-institute/bluebird/issues/62) Episode file logging is broken for non-absolute file paths
- [#63](https://github.com/alan-turing-institute/bluebird/issues/63) Upload scenario endpoint doesn't handle logging the file data

## [1.2.0] - 2019-06-06

### Added

- `EPLOG` endpoint for pulling the logfile for the current episode
- `SCENARIO` endpoint for uploading a new scenario
- `SHUTDOWN` endpoint to stop BlueBird, and optionally stop the simulation server
- Framework for integration tests using Docker with BlueSky

### Changed

- Changed location of logs when running inside docker
- Changed BlueSky submodule to point to tag `turing-1.1.0`

### Fixed

- Prevent any local logs from being copied when running inside Docker
- Fix error when logging scenario file contents
- [#50](https://github.com/alan-turing-institute/bluebird/issues/50) Remove aircraft from BlueBird once BlueSky removes them

## [1.1.3] - 2019-05-09

### Added

- Make console logging level configurable
- Added service names and dependency to docker-compose file

### Fixed

- Fixed bug from [Core#70](https://github.com/alan-turing-institute/nats/issues/70)

## 1.1.2 (Not published)

## [1.1.1] - 2019-05-01

### Added

- Added hotfix branches to Travis config
- Added `acid` and `sim_t` to the response from `LISTROUTE`
- Added a version file for tracking

### Fixed

- Fixed case where some responses from BlueSky were being interpreted as errors

## [1.1.0] - 2019-04-17 - PR [#51](https://github.com/alan-turing-institute/bluebird/pull/51)
## [1.0.0] - 2019-03-26 - PR [#47](https://github.com/alan-turing-institute/bluebird/pull/47)

[Unreleased]: https://github.com/alan-turing-institute/bluebird/compare/2.0.2...develop
[2.0.2]: https://github.com/alan-turing-institute/bluebird/compare/2.0.1...2.0.2
[2.0.1]: https://github.com/alan-turing-institute/bluebird/compare/2.0.0...2.0.1
[2.0.0]: https://github.com/alan-turing-institute/bluebird/compare/1.3.0...2.0.0
[1.3.0]: https://github.com/alan-turing-institute/bluebird/compare/1.2.1...1.3.0
[1.2.1]: https://github.com/alan-turing-institute/bluebird/compare/1.2.0...1.2.1
[1.2.0]: https://github.com/alan-turing-institute/bluebird/compare/1.1.3...1.2.0
[1.1.3]: https://github.com/alan-turing-institute/bluebird/compare/1.1.1...1.1.3
[1.1.1]: https://github.com/alan-turing-institute/bluebird/compare/1.1.0...1.1.1
[1.1.0]: https://github.com/alan-turing-institute/bluebird/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/alan-turing-institute/bluebird/releases/tag/1.0.0
