"""
Package for the BlueSky simulator client
"""

from semver import VersionInfo
from bluebird.sim_client.abstract_sim_client import AbstractSimClient

from .sim_client import SimClient, MIN_SIM_VERSION

assert issubclass(
    SimClient, AbstractSimClient
), "Expected SimClient to be defined as a subclass of AbstractSimClient"

assert isinstance(
    MIN_SIM_VERSION, VersionInfo
), "Expected MIN_SIM_VERSION to be an instance of VersionInfo"
