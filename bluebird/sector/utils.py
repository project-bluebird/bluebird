"""
Utility functions for the sector package
"""

import logging

import bluebird.cache as bb_cache
import bluebird.client as bb_client
import bluebird.settings as settings
from bluebird.utils.timer import Timer
import bluebird.utils as bb_utils


_SCALE_METRES_TO_FEET = 3.280839895

_LOGGER = logging.getLogger(__name__)


def check_active_sector() -> bool:

    idx = settings.SECTOR_IDX
    if idx == -1:
        _LOGGER.info(f"BB_SECTOR_IDX not set. All defined sectors will be monitored")
        return False

    if idx >= len(settings.SECTORS):
        raise ValueError(f"BB_SECTOR_IDX is larger than the number of defined sectors")

    _LOGGER.info(f"Monitoring BB_SECTOR_IDX={idx}")
    return True


def create_bluesky_areas():
    for sector in settings.SECTORS:
        cmd_str = (
            f"BOX {sector['name']} {sector['min_lat']} {sector['min_lon']} "
            f"{sector['max_lat']} {sector['max_lon']} {sector['min_alt']}  "
            f"{sector['max_alt']}"
        )
        _LOGGER.debug(cmd_str)
        err = bb_client.CLIENT_SIM.send_stack_cmd(cmd_str)
        if err:
            raise ValueError(err)


def create_bluesky_waypoints():
    for wpt in settings.WAYPOINTS:
        cmd_str = f"DEFWPT {wpt} {wpt['lat']} {wpt['lon']}"
        _LOGGER.debug(cmd_str)
        err = bb_client.CLIENT_SIM.send_stack_cmd(cmd_str)
        if err:
            raise ValueError(err)


def point_inside_sector(point) -> bool:
    """
    Checks if a point (lat, lon, alt) is inside the current active sector
    """

    # Don't care about sectors in this case, so every point is inside the global sector
    if settings.SECTOR_IDX == -1:
        return True

    sector = settings.SECTORS[settings.SECTOR_IDX]
    alt = point["alt"] * _SCALE_METRES_TO_FEET

    lat_ok = (sector["min_lat"] <= point["lat"]) and (point["lat"] <= sector["max_lat"])
    lon_ok = (sector["min_lon"] <= point["lon"]) and (point["lon"] <= sector["max_lon"])
    alt_ok = (sector["min_alt"] <= alt) and (alt <= sector["max_alt"])
    return lat_ok and lon_ok and alt_ok


class SectorWatcher:
    def __init__(self):

        if settings.SECTOR_IDX == -1:
            raise ValueError("Can only watch specific sub-sectors")

        self._logger = logging.getLogger(__name__)

        self._ac_in_sector = set()
        self._exit_points = {}

        self._timer = Timer(self.watch, 1)

    def start(self):
        self._timer.start()
        bb_utils.TIMERS.append(self._timer)

    def watch(self):

        current_ac_in_sector = set()
        for acid in bb_cache.AC_DATA.store:
            if point_inside_sector(bb_cache.AC_DATA.get(acid)[acid]):
                current_ac_in_sector.add(acid)

        # Check for new aircraft
        for new_acid in current_ac_in_sector - self._ac_in_sector:
            self._logger.debug(f"Aircraft {new_acid} has entered our sector")
            self._ac_in_sector.add(new_acid)

        # Check for missing aircraft
        for exited_acid in self._ac_in_sector - current_ac_in_sector:
            self._logger.debug(f"Aircraft {exited_acid} has exited our sector")
            self._ac_in_sector.remove(exited_acid)
            self._exit_points[exited_acid] = bb_cache.AC_DATA.get(exited_acid)[
                exited_acid
            ]

    def check_exited(self, acid):
        if acid in self._exit_points:
            return self._exit_points[acid]
        if acid in self._ac_in_sector:
            return f"Aircraft {acid} is in our sector, but has not exited yet"
        return f"Aircraft {acid} is not in our sector"
