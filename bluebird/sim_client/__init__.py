"""
Package for simulator clients and their associated logic
"""
import importlib.util
import logging
from typing import Tuple

from semver import VersionInfo

from bluebird.metrics import MetricsProviders
from bluebird.settings import Settings
from bluebird.utils.abstract_sim_client import AbstractSimClient


_LOGGER = logging.getLogger(__name__)

# NOTE(RKM 2019-11-26) Yes, I'm aware this is hack-y :^)
CLIENT_INIT_STR = """
from semver import VersionInfo
from bluebird.utils.abstract_sim_client import AbstractSimClient

# NOTE: Deliberate relative import here! Grabs the particular sim_client module for the
# sim implementation we are trying to load
from .sim_client import SimClient, MIN_SIM_VERSION

assert issubclass(
    SimClient, AbstractSimClient
), "Expected SimClient to be defined as a subclass of AbstractSimClient"

assert isinstance(
    MIN_SIM_VERSION, VersionInfo
), "Expected MIN_SIM_VERSION to be an instance of VersionInfo"
"""


def setup_sim_client(
    metrics_providers: MetricsProviders,
) -> Tuple[AbstractSimClient, VersionInfo]:
    """
    Imports and returns an instance of the AbstractSimClient class as specified by
    Settings.SIM_TYPE, and the minimum version of simulator that the client supports
    """

    mod_name = Settings.SIM_TYPE.name
    mod_path = f"{__package__}.{mod_name.lower()}"

    _LOGGER.info(f'Loading the "{mod_name}" simulator client')

    try:
        spec = importlib.util.find_spec(mod_path)
        if spec is None:
            raise ModuleNotFoundError(f"Can't find {mod_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            f"Couldn't import {mod_path}. Check the module exists and is valid"
        ) from exc

    if not hasattr(module, "SimClient") or not issubclass(
        module.SimClient, AbstractSimClient
    ):
        raise AttributeError(
            f"Module for {mod_name} does not contain a valid SimClient class"
        )

    try:
        sim_client = module.SimClient(metrics_providers=metrics_providers)
    except TypeError as exc:
        raise TypeError(
            f"Client class for {mod_name} does not properly implement the"
            " required AbstractSimClient methods"
        ) from exc

    return (sim_client, getattr(module, "MIN_SIM_VERSION"))
