"""
Package for simulator clients and their associated logic
"""

import importlib.util
import logging

from bluebird import settings as bb_settings
from .abstractsimclient import AbstractSimClient

_LOGGER = logging.getLogger(__name__)


def setup_sim_client(sim_state, ac_data) -> AbstractSimClient:
    """
	Imports and returns an instance of the AbstractSimClient class, as specified by	settings.SIM_TYPE
	:return:
	"""

    _LOGGER.info(f'Loading the "{bb_settings.SIM_TYPE.name}" simulator client')

    mod_path = f"{__package__}.{bb_settings.SIM_TYPE.name.lower()}"
    try:
        spec = importlib.util.find_spec(mod_path)
        if spec is None:
            raise ModuleNotFoundError(f"Can't find {mod_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except ModuleNotFoundError as exc:
        _LOGGER.info(f"Couldn't import {mod_path}. Check the module exists")
        raise exc

    if not hasattr(module, "SimClient") or not issubclass(
        module.SimClient, AbstractSimClient
    ):
        raise AttributeError("Loaded module does not contain a valid SimClient class")

    return module.SimClient(sim_state, ac_data)
