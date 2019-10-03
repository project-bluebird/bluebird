"""
Package for BlueBird's built-in metrics system
"""

from bluebird.metrics.abstract_metrics_provider import AbstractMetricProvider

from .provider import Provider

assert isinstance(
    Provider, AbstractMetricProvider
), "Expected Provider to be defined as a subclass of AbstractMetricProvider"

