import datetime

default_lifetime = datetime.timedelta(seconds=10)

def now():
    return datetime.datetime.utcnow()


def before(dt):
    return now() < dt
