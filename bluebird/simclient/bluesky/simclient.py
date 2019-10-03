"""
BlueSky simulation client class
"""

import os

from semver import VersionInfo

from bluebird.settings import Settings
from bluebird.simclient import AbstractSimClient
from .blueskyclient import BlueSkyClient

_BS_MIN_VERSION = os.getenv("BS_MIN_VERSION")
if not _BS_MIN_VERSION:
    raise ValueError("Error: the BS_MIN_VERSION environment variable must be set")

MIN_SIM_VERSION = VersionInfo.parse(_BS_MIN_VERSION)


class SimClient(AbstractSimClient):
    def __init__(self, sim_state, ac_data):
        self._client = BlueSkyClient(sim_state, ac_data)

    def start_timers(self):
        return [self._client.start_timer()]

    def connect(self, timeout=1):
        self._client.connect(
            Settings.SIM_HOST,
            event_port=Settings.BS_EVENT_PORT,
            stream_port=Settings.BS_STREAM_PORT,
            timeout=timeout,
        )

    @property
    def host_version(self):
        return self._client.host_version

    def stop(self):
        self._client.stop()
