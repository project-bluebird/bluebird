"""
Contains the MetricProvider abstract base class
"""

from abc import ABC, abstractmethod


class MetricProvider(ABC):

	def __init__(self):
		super().__init__()

	@abstractmethod
	def __call__(self, metric, *args, **kwargs):
		pass

	@abstractmethod
	def __str__(self):
		pass

	@abstractmethod
	def version(self):
		pass
