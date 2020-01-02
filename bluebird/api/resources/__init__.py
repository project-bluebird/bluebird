"""
Package provides logic for the simulation API endpoints
"""

# Aircraft control
from .addwpt import AddWpt
from .alt import Alt
from .cre import Cre
from .direct import Direct
from .hdg import Hdg
from .listroute import ListRoute
from .pos import Pos
from .spd import Spd

# Simulation control
from .defwpt import DefWpt
from .dtmult import DtMult
from .hold import Hold
from .loadlog import LoadLog
from .op import Op
from .reset import Reset
from .scenario import Scenario
from .sector import Sector
from .seed import Seed
from .step import Step

# BlueBird control
from .epinfo import EpInfo
from .eplog import EpLog
from .siminfo import SimInfo
from .shutdown import Shutdown

# Metrics
from .metrics import Metric
from .metrics import MetricProviders

# Keep flake8 happy :)
__all__ = [
    "AddWpt",
    "Alt",
    "Cre",
    "Direct",
    "Hdg",
    "ListRoute",
    "Pos",
    "Spd",
    "DefWpt",
    "DtMult",
    "Hold",
    "LoadLog",
    "Op",
    "Reset",
    "Scenario",
    "Sector",
    "Seed",
    "Step",
    "EpInfo",
    "EpLog",
    "SimInfo",
    "Shutdown",
    "Metric",
    "MetricProviders",
]
