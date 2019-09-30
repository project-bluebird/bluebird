"""
Provides logic for the Load Log API endpoint
"""

import logging
import os

import re
import time
import uuid
from flask import jsonify
from flask_restful import Resource, reqparse

import bluebird.settings
from bluebird.api.resources.utils import (
    check_ac_data,
    validate_scenario,
    wait_until_eq,
    bb_app,
)
from bluebird.logging import store_local_scn
from bluebird.utils.timeutils import timeit

_LOGGER = logging.getLogger(__name__)

PARSER = reqparse.RequestParser()
PARSER.add_argument("filename", type=str, location="json", required=False)
PARSER.add_argument("lines", type=str, location="json", required=False, action="append")
PARSER.add_argument("time", type=int, location="json", required=True)


def parse_lines(lines, target_time=0):
    """
	Parses the content of an episode file
	:param lines:
	:param target_time:
	:return: String for errors or dict with parsed data
	"""

    if not lines:
        return "No lines provided"

    lines = list(lines)  # Take a copy of the input

    # Get the seed from the first line
    match = re.match(r".*Episode started.*Seed is (\d+)", lines.pop(0))
    if not match:
        return "Episode seed was not set"
    scn_data = {"seed": int(match.group(1)), "lines": []}

    if not lines:
        return "No more lines after parsing seed"

    while not "Scenario file loaded" in lines[0]:
        lines.pop(0)
        if not lines:
            return "Couldn't find scenario content"

    lines.pop(0)

    while lines:
        match = re.match(r".*E.*>.*", lines[0])
        if not match:
            break
        scn_data["lines"].append(lines.pop(0).split(" E ")[1])

    if not lines:
        return "No more lines after parsing scenario content"

    while lines:
        line = lines.pop(0)
        if "Episode finished" in line:
            return scn_data
        match = re.match(r".*C \[(\d+)\] (.*)$", line)
        if match and not "STEP" in line:
            time_s = int(match.group(1))
            if not target_time or time_s <= target_time:
                cmd_time = time.strftime("%H:%M:%S", time.gmtime(time_s))
                cmd_str = match.group(2)
                scn_data["lines"].append(f"{cmd_time}> {cmd_str}")

    return "Could not find end of episode"


class LoadLog(Resource):
    """
	Contains logic for the Load Log endpoint
	"""

    @staticmethod
    @timeit("LoadLog")
    def post():
        """
		Logic for POST events. Returns the simulator to a previous state given a logfile
		:return: :class:`~flask.Response`
		"""

        if bluebird.settings.SIM_MODE != "agent":
            resp = jsonify("Can only be used in agent mode")
            resp.status_code = 400
            return resp

        parsed = PARSER.parse_args()
        if bool(parsed["filename"]) == bool(parsed["lines"]):
            resp = jsonify("Either filename or lines must be specified")
            resp.status_code = 400
            return resp

        target_time = parsed["time"]
        if target_time <= 0:
            resp = jsonify("Target time must be greater than 0")
            resp.status_code = 400
            return resp

        prev_dt = bb_app().sim_client.step_dt

        _LOGGER.debug("Starting log reload")

        # Reset now so the current episode log is closed
        err = bb_app().sim_client.reset_sim()

        if err:
            resp = jsonify(f"Simulation not reset: {err}")
            resp.status_code = 500

        if parsed["filename"]:
            if not os.path.exists(parsed["filename"]):
                resp = jsonify(f'Could not find episode file {parsed["filename"]}')
                resp.status_code = 400
                return resp
            lines = tuple(open(parsed["filename"], "r"))
        else:
            lines = parsed["lines"]

        _LOGGER.debug("Parsing log content")
        parsed_scn = parse_lines(lines, target_time)

        if isinstance(parsed_scn, str):
            resp = jsonify(f"Could not parse episode content: {parsed_scn}")
            resp.status_code = 400
            return resp

        # Assert that the requested time is not past the end of the log
        last_data = next(
            x for x in reversed(lines) if re.match(r".*A \[(\d+)\] (.*)$", x)
        )
        last_time = int(re.search(r"\[(.*)]", last_data).group(1))

        if target_time > last_time:
            resp = jsonify(
                f"Error: Target time was greater than the latest time in the log"
            )
            resp.status_code = 400
            return resp

        err = validate_scenario(parsed_scn["lines"])

        if err:
            resp = jsonify("Could not create a valid scenario from the given log")
            resp.status_code = 400
            return resp

        # All good - do the reload

        _LOGGER.debug("Setting the simulator seed")
        err = bb_app().sim_client.send_stack_cmd(f'SEED {parsed_scn["seed"]}')

        if err:
            resp = jsonify(f"Could not set seed {err}")
            resp.status_code = 500

        bb_app().sim_client.seed = parsed_scn["seed"]

        scn_name = f"reloads/{str(uuid.uuid4())[:8]}.scn"

        _LOGGER.debug("Uploading the new scenario")
        store_local_scn(scn_name, parsed_scn["lines"])
        err = bb_app().sim_client.upload_new_scenario(scn_name, parsed_scn["lines"])

        if err:
            resp = jsonify(f"Error uploading scenario: {err}")
            resp.status_code = 500

        _LOGGER.info("Starting the new scenario")
        err = bb_app().sim_client.load_scenario(scn_name, start_paused=True)

        if err:
            resp = jsonify(f"Could not start scenario after upload: {err}")
            resp.status_code = 500
            return resp

        _LOGGER.debug("Waiting for simulation to be paused")
        if not wait_until_eq(bb_app().sim_state.sim_state, 1):
            resp = jsonify(f"Could not pause simulation after starting new scenario")
            resp.status_code = 500
            return resp

        diff = target_time - bb_app().sim_state.sim_t
        if diff:
            # Naive approach - set DTMULT to target, then STEP once...
            _LOGGER.debug(f"Time difference is {diff}. Stepping to {target_time}")
            err = bb_app().sim_client.send_stack_cmd(f"DTMULT {diff}")

            if err:
                resp = jsonify(f"Could not change speed: {err}")
                resp.status_code = 500
                return resp

            _LOGGER.debug("Performing step")
            err = bb_app().sim_client.step()

            if err:
                resp = jsonify(f"Could not step simulation: {err}")
                resp.status_code = 500
                return resp
        else:
            _LOGGER.debug(f"Simulation already at required time")

        _LOGGER.debug("Waiting for ac_data to catch up")
        err_resp = check_ac_data()
        if err_resp:
            return err_resp

        bb_app().ac_data.log()

        # Reset DTMULT to the previous value
        err = bb_app().sim_client.send_stack_cmd(f"DTMULT {prev_dt}")

        if err:
            resp = jsonify(
                f"Episode reloaded, but could not reset DTMULT to previous value"
            )
            resp.status_code = 500
            return resp

        # TODO Do we want to check before/after positions here and check if the differences are
        # acceptable?

        resp = jsonify("Simulation reloaded")
        resp.status_code = 200
        return resp
