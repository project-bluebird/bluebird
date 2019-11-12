"""
Package for simulator clients and their associated logic
"""

import importlib.util
import logging

from bluebird.settings import Settings
from .abstract_sim_client import AbstractSimClient


_LOGGER = logging.getLogger(__name__)

_CLIENT_INIT_STR = """
from semver import VersionInfo
from bluebird.sim_client.abstract_sim_client import AbstractSimClient

from .sim_client import SimClient, MIN_SIM_VERSION

assert issubclass(
    SimClient, AbstractSimClient
), "Expected SimClient to be defined as a subclass of AbstractSimClient"

assert isinstance(
    MIN_SIM_VERSION, VersionInfo
), "Expected MIN_SIM_VERSION to be an instance of VersionInfo"
"""


# TODO: We should be able to annotate this as returning a Tuple[AbstractSimClientType,
# VersionInfo], but the current typing implementation seems to not like that...
def setup_sim_client():
    """
    Imports and returns an instance of the AbstractSimClient class, as specified by
    Settings.SIM_TYPE
    :return:
    """

    _LOGGER.info(f'Loading the "{Settings.SIM_TYPE.name}" simulator client')

    mod_path = f"{__package__}.{Settings.SIM_TYPE.name.lower()}"
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
        raise AttributeError("Loaded module does not contain a valid SimClient class")

    try:
        sim_client = module.SimClient()
    except TypeError as exc:
        raise TypeError(
            f"Client class for {Settings.SIM_TYPE.name} does not properly implement the"
            " required AbstractSimClient methods"
        ) from exc

    return (sim_client, getattr(module, "MIN_SIM_VERSION"))