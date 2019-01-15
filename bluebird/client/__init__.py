"""
Contains objects for communicating with the client simulation
"""

import os
import sys

# Import BlueSky from the git submodule
sys.path.append(
				os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.abspath('./bluesky')))

# pylint: disable=C0413
from .client import ApiClient

# Global reference to the client
CLIENT_SIM = ApiClient()
