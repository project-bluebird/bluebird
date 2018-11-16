import os

import sys

# Import BlueSky from the git submodule
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.abspath('./bluesky')))

from .client import ApiClient
