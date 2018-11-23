from threading import Thread, Event
from time import sleep


class Timer(Thread):
    """ Simple timer. Calls the given method periodically """

    def __init__(self, method, tickrate, *args, **kwargs):
        Thread.__init__(self)
        self.event = Event()
        self.tickrate = tickrate  # Seconds
        self.cmd = lambda: method(*args, **kwargs)

    def run(self):
        while not self.event.is_set():
            self.cmd()
            sleep(self.tickrate)

    def stop(self):
        self.event.set()
