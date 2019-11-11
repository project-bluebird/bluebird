"""
Contains the class for storing aircraft data which is streamed from the simulation
"""

import datetime
import json
import logging
from typing import Dict, List

import bluebird.logging
from bluebird.settings import Settings
from bluebird.utils.timer import Timer
from bluebird.utils.timeutils import log_rate
from bluebird.utils.types import Altitude, Callsign
from bluebird.utils.properties import AircraftProperties

LOG_PREFIX = "A"

# Note on unit precision:
#   lat/lon 5 d.p. is ~1.1 meters, so can round to 5 places
#   gs      1 knot is ~0.5 m/s, so can store as an int
#   vs      1 fpm  is ~0.005 m/s, so can store as an int

# TODO
# def reset(self):
#     """
#     Resets the cache for a new episode
#     :return
#     """
#     super().clear()
#     self.cleared_fls = {}
#     self.timer.disabled = True
#     self.have_logged_aircraft = False


class AircraftDataCache:
    """
    Holds the most recent aircraft data
    """

    @property
    def store(self) -> Dict[Callsign, AircraftProperties]:
        """
        Returns the whole aircraft data cache
        """
        return self._store

    def __init__(self):

        self._logger = logging.getLogger(__name__)

        self._store: Dict[Callsign, AircraftProperties] = {}

        # Periodically log the sim state to file. Starts disabled.
        self._target_sim_speed = 1

        # self._timer = Timer(self.log, Settings.SIM_LOG_RATE)
        # self._timer.disabled = True

        self.have_logged_aircraft = False
        self.prev_log_sim_t = 0

        self.cleared_fls = {}

    def clear(self):
        """
        Clears the cache
        """
        self._store.clear()

    def contains(self, callsign: Callsign) -> bool:
        """
        Check if the given callsign exists in the cache
        :return:
        """
        return callsign in self._store

    def get_all_properties(self) -> List[AircraftProperties]:
        return list(self._store.values())

    def set_cleared_fl(self, callsign: Callsign, flight_level: Altitude) -> None:
        """
        Update the cleared flight level for an aircraft
        :param callsign:
        :param flight_level:
        :return:
        """
        if not callsign in self._store:
            raise KeyError("Aircraft {callsign} is not in the cache")
        self._store[callsign].cleared_flight_level = flight_level


### Old methods ###

# def start_timer(self):
#     """
#     Starts the timer for logging
#     :return:
#     """

#     self._timer.start()
#     return self._timer

# def fill(self, data):

#     current_acids = set(self.store)
#     new_acids = set()

#     # Unsure if this is needed
#     if isinstance(data, dict) and "id" in data:
#         for idx in range(len(data["id"])):
#             acid = data["id"][idx]
#             new_acids.add(acid)
#             ac_data = {
#                 "actype": data["actype"][idx],
#                 "alt": int(data["alt"][idx]),
#                 "lat": round(data["lat"][idx], 5),
#                 "lon": round(data["lon"][idx], 5),
#                 "gs": int(data["gs"][idx]),
#                 "vs": int(data["vs"][idx]),
#             }

#             self.store[acid] = ac_data

#     # If any aircraft have been removed
#     for acid in current_acids - new_acids:
#         del self.store[acid]

#     # Set any initial cleared flight levels
#     for missing in current_acids - self.cleared_fls.keys():
#         self.cleared_fls[missing] = self.store[missing]["alt"]

# def resume_log(self):
#     """
#     Resumes the episode log at the previous rate
#     :return:
#     """
#     # TODO: Don't set DTMULT in sim files!
#     self.set_log_rate(self._target_sim_speed)

# def set_log_rate(self, new_speed, new_log=False):
#     """
#     Set the speed at which simulation data is logged at
#     :param new_speed:
#     :param new_log:
#     :return:
#     """

#     self._target_sim_speed = new_speed
#     current_speed = self._sim_state.sim_speed

#     rate = log_rate(new_speed)

#     if new_log or (new_speed > 0 and current_speed == 0):
#         state = "started" if new_log else "resumed"
#         self._logger.info(f"Simulation {state}. Log rate: {rate}")
#         self.timer.set_tickrate(rate)
#         self.timer.disabled = False
#         return

#     if new_speed == 0 and current_speed != 0:
#         self._logger.info("Simulation paused")
#         self.timer.disabled = True
#         return

#     if current_speed != new_speed:
#         self._logger.info(
#             f"Sim speed changed: {current_speed}x -> {new_speed}x. New "
#             f"log rate: {rate}"
#         )
#         self._timer.set_tickrate(rate)
#         return

# def log(self):
#     """
#     Writes the current aircraft states to the episode log
#     :return:
#     """

#     if not self.store:
#         return

#     sim_t = self._sim_state.sim_t

#     # Don't log if the simulation hasn't advanced, except if it is the initial log
#     if sim_t == self.prev_log_sim_t and self.have_logged_aircraft:
#         return

#     self.have_logged_aircraft = True
#     self.prev_log_sim_t = sim_t

#     # TODO Tidy this up
#     data = dict(self.store)
#     for aircraft in data.keys():  # pylint: disable=consider-iterating-dictionary
#         for prop in list(data[aircraft].keys()):
#             if prop.startswith("_"):
#                 del data[aircraft][prop]
#                 continue
#             if isinstance(data[aircraft][prop], datetime.datetime):
#                 data[aircraft][prop] = str(data[aircraft][prop].utcnow())

#     json_data = json.dumps(data, separators=(",", ":"))
#     bluebird.logging.EP_LOGGER.debug(
#         f"[{sim_t}] {json_data}", extra={"PREFIX": LOG_PREFIX}
#     )
