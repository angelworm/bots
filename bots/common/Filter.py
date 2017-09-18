
from multiprocessing import Process, Queue
from queue import Empty, Full
import collections

from .Status import Status

class Pusher:
    def __init__(self):
        self.targets = dict()

    def put(self, status):
        assert isinstance(status, Status)

        if status.type in self.targets:
            for Q in self.targets[status.type]:
                try:
                    Q.put(status, False)
                except Full as e:
                    pass

    def subscribe(self, statustype, Q):
        Qs = self.targets.get(statustype, [])
        Qs.append(Q)
        self.targets[statustype] = Qs

class FilterSubscribeException(Exception):
    pass

class FilterBase(Process):
    def __init__(self, filtername):
        super().__init__(name = filtername, daemon = True)

        self.filtername = filtername
        self.iQ = Queue()
        self.Q = Pusher()

    def run(self):
        self.run_()

    def run_(self):
        while True:
            message = self.iQ.get()
            try:
                self.onmessage(message)
            except Exception as e:
                print(e)

    def onmessage(self, message):
        pass

    def subscribe(self, statustype, f):
        if not isinstance(f, FilterBase):
            raise FilterSubscribeException
        self.Q.subscribe(statustype, f.iQ)
