"""
Package contains BlueBird's metrics code
"""

import importlib
import importlib.util
import logging

import bluebird.settings as bb_settings

_LOGGER = logging.getLogger(__package__)

METRIC_PROVIDERS = []


def setup_metrics():
	"""
	Loads the metrics providers defined in the global settings
	:return:
	"""

	for provider in bb_settings.METRICS_PROVIDERS:
		mod_path = f'{__package__}.{provider}.provider'
		try:
			spec = importlib.util.find_spec(mod_path)
			if spec is None:
				raise ModuleNotFoundError(f'Can\'t find {mod_path}')
			else:
				module = importlib.util.module_from_spec(spec)
				spec.loader.exec_module(module)
				METRIC_PROVIDERS.append(getattr(module, 'Provider')())
		except ModuleNotFoundError as exc:
			_LOGGER.error(f'Couldn\'t import {mod_path}. Check the module exists')
			raise exc
