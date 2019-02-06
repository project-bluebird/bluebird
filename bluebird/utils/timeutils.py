"""
Contains utility functions for dates and times
"""

import datetime
import time

DEFAULT_LIFETIME = datetime.timedelta(seconds=10)


def before(date_time):
	"""
	Check if the given time has passed (i.e. before now())
	:param date_time: The datetime to test
	:return: If the given datetime is in the past
	"""

	return now() < date_time


def now():
	"""
	Returns the current datetime in UTC
	:return: DateTime
	"""

	return datetime.datetime.utcnow()


def wait_until(condition, *args, interval=0.1, timeout=1):
	"""
	Sleeps until the given condition is met
	:param condition: The method to check the condition on
	:param args: Any arguments to pass to the method
	:param interval: The rate in seconds at which the condition is checked
	:param timeout: The maximum amount of time in seconds to wait for the condition to be met
	"""

	start = time.time()
	while not condition(*args) and time.time() - start < timeout:
		time.sleep(interval)
