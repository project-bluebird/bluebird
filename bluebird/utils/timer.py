"""
Contains a utility Timer class
"""

from threading import Event, Thread
from time import sleep


class Timer(Thread):
	"""
	Simple timer which calls the given method periodically
	"""

	def __init__(self, method, tickrate, *args, **kwargs):
		"""
		:param method: The method to call periodically
		:param tickrate: The rate in seconds at which the method is called
		:param args: Positional arguments to call the method with
		:param kwargs: Keyword arguments to call the method with
		"""

		Thread.__init__(self)
		self.event = Event()
		self.tickrate = tickrate  # Seconds
		self.cmd = lambda: method(*args, **kwargs)

	def run(self):
		"""
		Start the timer
		"""

		while not self.event.is_set():
			self.cmd()
			sleep(self.tickrate)

	def stop(self):
		"""
		Stop the timer and ensure the thread is joined
		"""

		self.event.set()
