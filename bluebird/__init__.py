"""
BlueBird package
"""

# TODO(RKM 2019-12-19) Move the logging initialization code here so we don't have to
# import it first
from bluebird import logging  # noqa: F401
from bluebird.bluebird import BlueBird

__all__ = [BlueBird]
