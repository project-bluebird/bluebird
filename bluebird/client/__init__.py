"""
Contains objects for communicating with the client simulation
"""

import os
import sys

from .client import ApiClient

# Import BlueSky from the git submodule
sys.path.append(
				os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.abspath('./bluesky')))

# Global reference to the client
CLIENT_SIM = ApiClient()
