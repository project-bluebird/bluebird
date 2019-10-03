"""
MachColl simulation client class
"""

from semver import VersionInfo
from bluebird.simclient import AbstractSimClient

# TODO Need to check version of MachColl
MIN_SIM_VERSION = VersionInfo.parse("0.0.0")


class SimClient(AbstractSimClient):
    pass
