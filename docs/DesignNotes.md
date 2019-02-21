
# Design Notes

## Module layout

```
bluebird/
  - api/			# Flask server & API definitions
    - resources/	# API Resource endpoints. One file per endpoint
    - static/		# Static routes. Currently serves README.md only
  - cache/ 			# Cache objects used to store simulation state
  - client/			# Simulation client classes
  - utils/ 			# Utility functions
  bluebird.py		# Bluebird application class
  settings.py		# Default app settings
run.py      		# Entry point
```
