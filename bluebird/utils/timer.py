from threading import Thread, Event
from time import sleep


class Timer(Thread):
    """ Simple timer. Calls the given method periodically """

    def __init__(self, method, tickrate):
        Thread.__init__(self)

        self.event = Event()
        self.method = method
        self.tickrate = tickrate  # Seconds

    def run(self):
        while not self.event.is_set():
            self.method()
            sleep(self.tickrate)

    def stop(self):
        self.event.set()
