
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/alan-turing-institute/bluebird/compare/1.1.3...develop
[1.1.3]: https://github.com/alan-turing-institute/bluebird/compare/1.1.1...1.1.3
[1.1.1]: https://github.com/alan-turing-institute/bluebird/compare/1.1.0...1.1.1
[1.1.0]: https://github.com/alan-turing-institute/bluebird/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/alan-turing-institute/bluebird/releases/tag/1.0.0
