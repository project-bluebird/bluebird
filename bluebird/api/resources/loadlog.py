"""
Provides logic for the Load Log API endpoint
"""

# TODO Tidy this up
# pylint: disable=too-many-return-statements, too-many-branches, too-many-statements

import logging
import os
import re
import time
from typing import Union
import uuid

from flask_restful import Resource, reqparse

import bluebird.api.resources.utils.responses as responses
from bluebird.api.resources.utils.utils import (
    validate_scenario,
    parse_args,
    is_agent_mode,
    sim_proxy,
)
from bluebird.logging import store_local_scn
from bluebird.utils.timeutils import timeit
from bluebird.settings import Settings
from bluebird.utils.properties import SimType


_LOGGER = logging.getLogger(__name__)

_PARSER = reqparse.RequestParser()
_PARSER.add_argument("filename", type=str, location="json", required=False)
_PARSER.add_argument(
    "lines", type=str, location="json", required=False, action="append"
)
_PARSER.add_argument("time", type=int, location="json", required=True)


# TODO Move this to the BlueSky client
def parse_lines(lines: list, target_time: int = 0) -> Union[str, dict]:
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

    if not lines:
        return "No more lines after parsing seed"

    while not "Scenario file loaded" in lines[0]:
        lines.pop(0)
        if not lines:
            return "Couldn't find scenario content"

    lines.pop(0)
    scn_data = {"seed": int(match.group(1)), "lines": []}

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
        :return:
        """

        if not is_agent_mode():
            return responses.bad_request_resp("Can only be used in agent mode")

        if Settings.SIM_TYPE != SimType.BlueSky:
            return responses.bad_request_resp(
                f"Method not supported for the {Settings.SIM_TYPE} simulator"
            )

        req_args = parse_args(_PARSER)

        if bool(req_args["filename"]) == bool(req_args["lines"]):
            return responses.bad_request_resp(
                "Either filename or lines must be specified"
            )

        target_time = req_args["time"]
        if target_time <= 0:
            return responses.bad_request_resp("Target time must be greater than 0")

        prev_dt = sim_proxy().sim_properties.sim_speed

        _LOGGER.debug("Starting log reload")

        # Reset now so the current episode log is closed
        err = sim_proxy().reset_sim()

        if err:
            return responses.internal_err_resp(f"Simulation not reset: {err}")

        if req_args["filename"]:
            if not os.path.exists(req_args["filename"]):
                return responses.bad_request_resp(
                    f'Could not find episode file {req_args["filename"]}'
                )
            with open(req_args["filename"], "r") as log_file:
                lines = list(log_file)
        else:
            lines = req_args["lines"]

        _LOGGER.debug("Parsing log content")
        parsed_scn = parse_lines(lines, target_time)

        if isinstance(parsed_scn, str):
            return responses.bad_request_resp(
                f"Could not parse episode content: {parsed_scn}"
            )

        # TODO Move regex to outer scope and comment
        # Assert that the requested time is not past the end of the log
        last_data = next(
            x for x in reversed(lines) if re.match(r".*A \[(\d+)\] (.*)$", x)
        )
        last_time = int(re.search(r"\[(.*)]", last_data).group(1))

        if target_time > last_time:
            return responses.bad_request_resp(
                f"Error: Target time was greater than the latest time in the log"
            )

        err = validate_scenario(parsed_scn["lines"])

        if err:
            return responses.bad_request_resp(
                "Could not create a valid scenario from the given log"
            )

        # All good - do the reload

        _LOGGER.debug("Setting the simulator seed")
        err = sim_proxy().set_seed(int(parsed_scn["seed"]))

        if err:
            return responses.internal_err_resp(f"Could not set seed {err}")

        scn_name = f"reloads/{str(uuid.uuid4())[:8]}.scn"

        _LOGGER.debug("Uploading the new scenario")
        store_local_scn(scn_name, parsed_scn["lines"])
        err = sim_proxy().upload_new_scenario(scn_name, parsed_scn["lines"])

        if err:
            return responses.internal_err_resp(f"Error uploading scenario: {err}")

        _LOGGER.info("Starting the new scenario")
        err = sim_proxy().load_scenario(scn_name, start_paused=True)

        if err:
            return responses.internal_err_resp(
                f"Could not start scenario after upload {err}"
            )

        diff = target_time - sim_proxy().sim_properties.sim_t

        if diff:
            # Naive approach - set DTMULT to target, then STEP once...
            _LOGGER.debug(f"Time difference is {diff}. Stepping to {target_time}")
            err = sim_proxy().set_sim_speed(diff)
            if err:
                return responses.internal_err_resp(f"Could not change speed: {err}")

            _LOGGER.debug("Performing step")
            err = sim_proxy().step_sim()

            if err:
                return responses.internal_err_resp(f"Could not step simulations: {err}")

        else:
            _LOGGER.debug(f"Simulation already at required time")

        # Reset DTMULT to the previous value
        err = sim_proxy().set_sim_speed(prev_dt)
        if err:
            return responses.internal_err_resp(
                "Episode reloaded, but could not reset DTMULT to previous value"
            )

        # TODO Do we want to check before/after positions here and check if the
        # differences are acceptable?

        return responses.ok_resp()
