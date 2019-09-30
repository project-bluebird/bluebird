"""
Contains utility functions for manipulating strings
"""

import re


def is_acid(string):
    """
	Checks if the given string is a valid aircraft identifier
	:param string: String to test
	:return: If the string is a valid aircraft identifier
	"""

    return re.match(r"[a-z0-9]{3,}", string, re.IGNORECASE)
