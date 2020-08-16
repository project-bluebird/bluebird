"""
Contains the BlueSky client class
"""
# TODO(RKM 2019-11-21) Check all the proxy layer comments
import json
import logging
import os
import re
import sys
import time
from copy import deepcopy
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import msgpack
import zmq

from bluebird.settings import Settings
from bluebird.utils.timer import Timer
from bluebird.utils.timeutils import timeit


# Import BlueSky from the specified path. Should default to the included submodule
_BS_PATH = os.getenv("BS_PATH", None)
assert _BS_PATH, "Expected BS_PATH to be set. Check your .env file"
_BS_PATH = Path(_BS_PATH)
assert _BS_PATH.is_dir() and "bluesky" in os.listdir(_BS_PATH), (
    "Expected BS_PATH to point to the root BlueSky directory. If this is your "
    "first time running BlueBird, try running this inside the root directory: "
    "'git submodule update --init'."
)
sys.path.append(str(_BS_PATH.resolve()))

from bluesky.network.client import Client  # noqa: E402
from bluesky.network.npcodec import decode_ndarray  # noqa: E402


CMD_LOG_PREFIX = "C"

# The BlueSky streams we subscribe to. 'ROUTEDATA' is also available
ACTIVE_NODE_TOPICS = [b"ACDATA", b"SIMINFO", b"ROUTEDATA"]

# Same rate as GuiClient polls for its data
POLL_RATE = 50  # Hz

# Events which should be ignored
IGNORED_EVENTS = [b"DEFWPT", b"DISPLAYFLAG", b"PANZOOM", b"SHAPE"]

# Tuple of regexes used to match responses from BlueSky that we can ignore
IGNORED_RESPONSES_RE = (
    re.compile("AREA"),
    re.compile("BlueSky Console Window"),
    re.compile("DEFWPT:.*added to navdb"),
    re.compile("IC: Opened"),
    re.compile("TIME"),
    re.compile("Unknown command: METRICS"),
)


class BlueSkyClient(Client):
    """Client class for the BlueSky simulator"""

    @property
    def aircraft_stream_data(self):
        return deepcopy(self._aircraft_stream_data)

    @property
    def sim_info_stream_data(self):
        return deepcopy(self._sim_info_data)

    def __init__(self):
        super().__init__(ACTIVE_NODE_TOPICS)
        self._logger = logging.getLogger(__name__)
        self._aircraft_stream_data = {}
        self._sim_info_data: List = []
        self._route_data: Dict[str, Any] = {}

        # Continually poll for the sim state
        self.timer = Timer(self.receive, POLL_RATE)

        # self.seed = None
        # self.step_dt = 1

        self._have_connection = False
        self._reset_flag = False
        self._echo_data = []
        self._scn_response = None
        self._awaiting_exit_resp = False
        self._last_stream_time = None

    def connect(self, *args, **kwargs):
        super().connect(*args, **kwargs)
        timeout = time.time() + 5
        while True:
            self.receive()
            if self._have_connection:
                break
            time.sleep(0.1)
            if time.time() >= timeout:
                raise TimeoutError("No data received from BlueSky")

    def start_timers(self) -> List[Timer]:
        """Start the client timer"""
        self.timer.start()
        return [self.timer]

    def stop(self):
        """Stop polling for the stream data"""
        self.timer.stop()
        # TODO(RKM 2019-11-21) Proxy layer should handle this
        # bluebird.logging.close_episode_log("client was stopped")

    def stream(self, name, data, sender_id):
        """Method called to process data received on a stream"""
        if name == b"ACDATA":
            self._aircraft_stream_data = data
        elif name == b"SIMINFO":
            self._sim_info_data = data
        # TODO(RKM 2019-11-22) BlueSky is not currently set-up to send route data for
        # all flights - only the ones that are "enabled" from the GUI...
        elif name == b"ROUTEDATA":
            self._route_data = data
        else:
            self._logger.warning(f'Unhandled data from stream "{name}"')

    def send_stack_cmd(self, data=None, response_expected=False, target=b"*"):
        """Send a command to the BlueSky simulation command stack"""

        # TODO(RKM 2019-11-21) Proxy layer should handle this
        # bluebird.logging.EP_LOGGER.debug(
        #     f"[{self._sim_state.sim_t}] {data}", extra={"PREFIX": CMD_LOG_PREFIX}
        # )

        self._echo_data = []
        self._logger.debug(f"STACKCMD: {data}")
        self.send_event(b"STACKCMD", data, target)

        time.sleep(25 / POLL_RATE)

        if response_expected and self._echo_data:
            # NOTE(rkm 2020-08-14) Return a copy of the current list
            return list(self._echo_data)

        if self._echo_data:
            self._logger.error(f"Command '{data}' resulted in error: {self._echo_data}")
            errs = "\n".join(str(x) for x in self._echo_data)
            return str(f"Error(s): {errs}")

        if response_expected:
            return "Error: no response received"

        return None

    def receive(self, timeout=0):
        try:
            socks = dict(self.poller.poll(timeout))
            if socks.get(self.event_io) == zmq.POLLIN:

                self._have_connection = True

                msg = self.event_io.recv_multipart()

                # Remove send-to-all flag if present
                if msg[0] == b"*":
                    msg.pop(0)

                route, eventname, data = msg[:-2], msg[-2], msg[-1]

                self.sender_id = route[0]
                route.reverse()
                pydata = (
                    msgpack.unpackb(data, object_hook=decode_ndarray, raw=False)
                    if data
                    else None
                )

                self._logger.debug(f"EVT :: {eventname} :: {pydata}")

                if eventname in IGNORED_EVENTS:
                    self._logger.debug(f"Ignored event {eventname}")

                # TODO Is this case relevant here?
                elif eventname == b"NODESCHANGED":
                    self.servers.update(pydata)
                    self.nodes_changed.emit(pydata)

                    # If this is the first known node, select it as active node
                    nodes_myserver = next(iter(pydata.values())).get("nodes")
                    if not self.act and nodes_myserver:
                        self.actnode(nodes_myserver[0])

                elif eventname == b"ECHO":
                    text = pydata["text"]
                    if not any(reg.match(text) for reg in IGNORED_RESPONSES_RE):
                        self._echo_data.append(text)
                    else:
                        self._logger.debug(f"Ignored echo text '{text}'")

                elif eventname == b"STEP":
                    # NOTE(rkm 2020-08-14) No longer need to handle this response since
                    # we check for the actual sim time being stepped (via SIMINFO)
                    pass

                elif eventname == b"RESET":
                    self._reset_flag = True

                elif eventname == b"QUIT":
                    if self._awaiting_exit_resp:
                        self._awaiting_exit_resp = False
                    else:
                        self._logger.error("Unhandled quit event from simulation")

                elif eventname == b"SCENARIO":
                    self._scn_response = pydata

                else:
                    self._logger.warning(
                        'Unhandled eventname "{} with data {}"'.format(
                            eventname, pydata
                        )
                    )
                    self.event(eventname, pydata, self.sender_id)

            if socks.get(self.stream_in) == zmq.POLLIN:

                self._last_stream_time = time.time()

                msg = self.stream_in.recv_multipart()

                strmname = msg[0][:-5]
                sender_id = msg[0][-5:]
                pydata = msgpack.unpackb(msg[1], object_hook=decode_ndarray, raw=False)

                self.stream(strmname, pydata, sender_id)

            # TODO(RKM 2019-11-26) This should probably be based on the stream frequency
            if self._last_stream_time:
                time_diff = time.time() - self._last_stream_time
                if time_diff > Settings.BS_STREAM_TIMEOUT:
                    raise TimeoutError(
                        f"Lost connection to BlueSky (time_diff={time_diff:.2f})"
                    )

            return True

        except zmq.ZMQError as exc:
            self._logger.error(exc)
            return False

    @timeit("BlueSkyClient")
    def upload_new_scenario(self, name: str, lines: List[str]):
        """Uploads a new scenario file to the BlueSky simulation"""

        self._scn_response = None

        data = json.dumps({"name": name, "lines": lines})
        self.send_event(b"SCENARIO", data)

        time.sleep(25 / POLL_RATE)

        resp = self._scn_response
        if resp == "Ok":
            return None
        return resp if resp else "No response received"

    def load_scenario(self, filename, start_paused=False) -> Optional[str]:
        """Load a scenario from a file"""

        # TODO(RKM 2019-11-21) Proxy layer should handle this
        # episode_id = bluebird.logging.restart_episode_log(self.seed)
        # self._logger.info(f"Episode {episode_id} started. Speed {speed}")
        # self._ac_data.set_log_rate(speed, new_log=True)

        self._reset_flag = False

        err = self.send_stack_cmd("IC " + filename)
        if err:
            return err

        err = self._await_reset_confirmation()
        if err:
            return err

        # NOTE(rkm 2020-01-03) BlueSky auto-starts if there are aircraft in a newly
        # loaded scenario. We could disable this "feature", however it seems linked to
        # other vital parts of BlueSky, so best leave it alone. This method gives
        # roughly the same result
        if start_paused:
            err = self.send_stack_cmd("HOLD")
            if err:
                return err

        return None

    def step(self):
        """Steps the simulation forward by one unit of DTMULT"""

        # TODO(RKM 2019-11-21) Proxy layer should handle this
        # init_t = int(self._sim_state.sim_t)
        # bluebird.logging.EP_LOGGER.debug(
        #     f"[{init_t}] STEP", extra={"PREFIX": CMD_LOG_PREFIX}
        # )
        # TODO(RKM 2019-11-21) Validate this

        init_t = self._sim_info_data[2]

        self.send_event(b"STEP")

        # Wait for the STEP response, and for the sim_t to have advanced
        wait_t = 1 / POLL_RATE
        timeout = time.time() + Settings.BS_TIMEOUT
        while time.time() < timeout:
            time.sleep(wait_t)
            if self._sim_info_data[2] > init_t:
                return None
        return "Error: Step command timed-out waiting for time to advance"

    def reset_sim(self) -> Optional[str]:
        """Resets the BlueSky sim and handles the response"""

        # TODO(RKM 2019-11-21) Proxy layer should handle this
        # self._ac_data.timer.disabled = True
        # bluebird.logging.close_episode_log("sim reset")

        self._reset_flag = False
        err = self.send_stack_cmd("RESET")
        return err if err else self._await_reset_confirmation()

    def _await_reset_confirmation(self):
        """Checks if a reset confirmation is received before the timeout"""

        timeout = time.time() + Settings.BS_TIMEOUT
        while time.time() < timeout:
            time.sleep(0.1)
            if self._reset_flag:
                return None
        return "Did not receive reset confirmation in time"

    def quit(self):
        """Sends a shutdown message to the simulation server"""

        self._awaiting_exit_resp = True
        self.send_event(b"QUIT", target=b"*")
        time.sleep(1)
        return not bool(self._awaiting_exit_resp)
