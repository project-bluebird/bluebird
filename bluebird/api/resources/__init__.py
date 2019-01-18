"""
Package provides logic for the simulation API endpoints
"""

# Aircraft control
from .alt import Alt
from .cre import Cre
from .hdg import Hdg
from .pos import Pos
from .spd import Spd
from .vs import Vs

# Simulation control
from .hold import Hold
from .ic import Ic
from .op import Op
