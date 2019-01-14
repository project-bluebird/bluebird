"""
Contains utility functions for debugging
"""

import sys


def errprint(text):
	"""
	Print text to stderr. Required to print to Flask console for now
	"""

	print(text, file=sys.stderr)
