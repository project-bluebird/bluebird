"""
Contains objects for communicating with the client simulation
"""

import os
import sys

# TODO This should be conditional on sim type
# Import BlueSky from the git submodule
sys.path.append(
				os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.abspath('./bluesky')))

# pylint: disable=wrong-import-position
from .client import ApiClient
