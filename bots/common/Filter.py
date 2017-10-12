
from multiprocessing import Process, Queue
from queue import Empty, Full
import collections
import traceback
import faulthandler

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
            self.log('start: PID:' + str(self.pid), level='INFO')
            try:
                self.run_()
            except Exception as e:
                self.log(traceback.format_exc())
            except BaseException:
                self.log(traceback.format_exc())
                raise

    def run_(self):
        while True:
            message = self.iQ.get()

            faulthandler.dump_traceback_later(60 * 1)
            try:
                self.onmessage(message)
            finally:
                faulthandler.cancel_dump_traceback_later()


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
