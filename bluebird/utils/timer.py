"""
Contains a utility Timer class
"""
import logging
import sys
from threading import Event
from threading import Thread
from time import sleep


class Timer(Thread):
    """Simple timer which calls the given method periodically"""

    def __init__(self, method, tickrate, *args, **kwargs):
        """
        :param method: The method to call periodically
        :param tickrate: The rate per second at which the method is called
        :param args: Positional arguments to call the method with
        :param kwargs: Keyword arguments to call the method with
        """

        Thread.__init__(self)
        self._event = Event()
        self._cmd = lambda: method(*args, **kwargs)

        self._check_rate(tickrate)
        self._sleep_time = 1 / tickrate

        self.disabled = False
        self._exited = False
        self._logger = logging.getLogger(
            f"{__name__}[{method.__module__}.{method.__name__}]"
        )
        self.exc_info = None

    def run(self):
        """
        Start the timer
        """

        self._logger.debug("Thread starting")
        try:
            while not self._event.is_set():
                if not self.disabled:
                    self._cmd()
                sleep(self._sleep_time)
        except Exception:
            self._logger.error("Thread threw an exception")
            self.exc_info = sys.exc_info()

        self._logger.debug("Thread exited")
        self._exited = True

    def set_tickrate(self, rate):
        """Set the timer tickrate"""

        self._check_rate(rate)
        self._sleep_time = 1 / rate

    def stop(self):
        """Stop the timer and ensure the thread is joined"""

        self._event.set()

        while not self._exited:
            break

    @staticmethod
    def _check_rate(rate):
        if rate <= 0:
            raise ValueError("Rate must be positive")
