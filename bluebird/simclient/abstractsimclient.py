"""
Contains the AbstractSimClient class
"""

from abc import ABC, abstractmethod

from semver import VersionInfo
from typing import Iterable

from bluebird.utils.timer import Timer


class AbstractSimClient(ABC):
	"""
	Adapter class to provide a common interface between BlueBird and the different simulator clients
	"""

	@abstractmethod
	def start_timers(self) -> Iterable[Timer]:
		"""
		Start any timed functions, and return all the Timer instances
		:return:
		"""
		pass

	@abstractmethod
	def connect(self, timeout=1) -> None:
		"""
		Connect to the simulation server
		:param timeout:
		:raises TimeoutException: If the connection could not be made before the timeout
		:return:
		"""
		pass

	@property
	@abstractmethod
	def host_version(self) -> VersionInfo:
		"""
		Return the version of the connected simulation server
		:return:
		"""
		pass

	@abstractmethod
	def stop(self) -> None:
		"""
		Disconnect from the simulation server, and stop the client (including any timers).
		:return:
		"""
		pass
