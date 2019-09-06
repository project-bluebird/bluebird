"""
Contains utility functions for BlueBird
"""

from types import TracebackType
from typing import Optional, Tuple, Type

from .timer import Timer

TIMERS = []

def check_timers()-> Optional[Tuple[Optional[Type[BaseException]], Optional[BaseException], Optional[TracebackType]]]:
	return next((x.exc_info for x in TIMERS if x.exc_info), None)
