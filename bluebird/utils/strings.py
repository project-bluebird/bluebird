import re


def is_acid(string):
    return re.match(r"[a-z0-9]{3,}", string, re.IGNORECASE)
