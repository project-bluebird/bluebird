"""
BlueSky simulation client class
"""

import bluebird.settings as bb_settings
from bluebird.simclient import AbstractSimClient
from .blueskyclient import BlueSkyClient


class SimClient(AbstractSimClient):
    def __init__(self, sim_state, ac_data):
        self._client = BlueSkyClient(sim_state, ac_data)

    def start_timers(self):
        return [self._client.start_timer()]

    def connect(self, timeout=1):
        self._client.connect(
            bb_settings.SIM_HOST,
            event_port=bb_settings.BS_EVENT_PORT,
            stream_port=bb_settings.BS_STREAM_PORT,
            timeout=timeout,
        )

    @property
    def host_version(self):
        return self._client.host_version

    def stop(self):
        self._client.stop()
