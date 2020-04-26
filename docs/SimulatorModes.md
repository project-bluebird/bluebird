
# BlueBird Simulator Modes

BlueBird can be set to run in one of two modes. The mode can be set when the app is launched with the `--sim_mode` CLI argument. The mode can also be changed during operation with the `SIMMODE` endpoint.

## `Sandbox` mode

The default mode. BlueBird acts purely as an API to the aircraft simulation, and scenarios are loaded and run normally.

## `Agent` mode

BlueBird acts as the controller of the aircraft simulation. Scenarios are loaded in a paused state, and must manually be advanced with the `STEP` endpoint.

The `STEP` endpoint advances the simulation in increments of the `DTMULT` setting. To use it:

- Set BlueBird to agent mode
- Load a scenario. This will be started in a paused state
- Set `DTMULT` to the required step size
- Call the `STEP` endpoint
