"""
Contains the import logic for MCClientMetrics
"""
import logging
import os
import sys


_LOGGER = logging.getLogger(__name__)

# Attempt to import the MCClientMetrics class from the nats.mc_client module, fallback
# to MC_PATH if needed

try:
    from nats.mc_client.mc_client_metrics import MCClientMetrics

    _LOGGER.debug(f"Imported MCClientMetrics from pip package")
except ModuleNotFoundError:
    _LOGGER.warning(
        "Could not find the nats package in sys.path. Attempting to look in "
        "MC_PATH instead"
    )
    _MC_PATH = os.getenv("MC_PATH", None)
    assert _MC_PATH, "Expected MC_PATH to be set. Check the .env file"
    _MC_PATH = os.path.abspath(_MC_PATH)
    assert os.path.isdir(_MC_PATH) and "nats" in os.listdir(
        _MC_PATH
    ), "Expected MC_PATH to point to the root nats directory"
    sys.path.append(_MC_PATH)
    from nats.mc_client.mc_client_metrics import MCClientMetrics  # noqa: F401
