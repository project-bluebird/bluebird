import datetime
import time

default_lifetime = datetime.timedelta(seconds=10)


def before(dt):
    return now() < dt


def now():
    return datetime.datetime.utcnow()


def wait_until(condition, interval=0.1, timeout=1, *args):
    start = time.time()
    while not condition(*args) and time.time() - start < timeout:
        time.sleep(interval)
