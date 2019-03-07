"""
Contains objects for storing simulation state
"""

AC_DATA = SIM_STATE = None

from .acdatacache import AcDataCache
from .sim_state import SimState

# Global store of aircraft data
AC_DATA = AcDataCache()

# Global store of the simulation state
SIM_STATE = SimState()
