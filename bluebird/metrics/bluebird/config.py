"""
Configuration for BlueBird's built-in evaluation metrics
"""

# TODO Proper support for units

LOS_SCORE = -1  # Score below the minimum separation

# Vertical separation (ft)
VERT_MIN_DIST = 1000
VERT_WARN_DIST = 2 * VERT_MIN_DIST

# Horizontal separation (nm)
HOR_MIN_DIST = 5
HOR_WARN_DIST = 2 * HOR_MIN_DIST
