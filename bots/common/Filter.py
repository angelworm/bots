
from multiprocessing import Process, Queue
from queue import Empty, Full
import collections
import traceback

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
        while True:
            try:
                self.run_()
            except Exception as e:
                self.log(traceback.format_exc())

    def run_(self):
        while True:
            message = self.iQ.get()
            self.onmessage(message)

    def onmessage(self, message):
        pass

    def subscribe(self, statustype, f):
        if not isinstance(f, FilterBase):
            raise FilterSubscribeException
        self.Q.subscribe(statustype, f.iQ)

    def log(self, message, level="ERROR"):
        status = Status(self.filtername, 'sys.log', {
            'level': level,
            'message': message
        })
        self.Q.put(status)
