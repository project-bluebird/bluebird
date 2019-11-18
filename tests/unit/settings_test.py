"""
Tests for the settings module
"""

from bluebird.utils.properties import SimMode
import bluebird.settings
from bluebird.settings import Settings


def test_can_update_settings():
    """Checks that imports of the global Settings object track any updates"""
    Settings.SIM_MODE = SimMode.Sandbox
    settings = getattr(bluebird.settings, "Settings")
    settings.SIM_MODE = SimMode.Agent
    assert Settings.SIM_MODE == SimMode.Agent
