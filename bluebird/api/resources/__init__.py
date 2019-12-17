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
from .vs import Vs

# Simulation control
from .defwpt import DefWpt
from .dtmult import DtMult
from .hold import Hold
from .ic import Ic
from .loadlog import LoadLog
from .op import Op
from .reset import Reset
from .sector import Sector
from .seed import Seed
from .step import Step
from .time import Time
from .upload_scenario import UploadScenario
from .upload_sector import UploadSector

# BlueBird control
from .epinfo import EpInfo
from .eplog import EpLog
from .siminfo import SimInfo
from .simmode import SimMode
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
    "Vs",
    "DefWpt",
    "DtMult",
    "Hold",
    "Ic",
    "LoadLog",
    "Op",
    "Reset",
    "Sector",
    "Seed",
    "Step",
    "Time",
    "UploadScenario",
    "UploadSector",
    "EpInfo",
    "EpLog",
    "SimInfo",
    "SimMode",
    "Shutdown",
    "Metric",
    "MetricProviders",
]
