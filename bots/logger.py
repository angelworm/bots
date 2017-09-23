
from multiprocessing import Process, Queue
from queue import Empty, Full
import collections
import traceback
import datetime

from bots.common import Status, FilterBase

class FileLogger(FilterBase):
    def __init__(self, confs):
        super().__init__(confs['filtername'])
        self.logdir = confs.get('dir', '.')
        self.logfile = confs.get('file', '{}.log'.format(self.filtername))
        self.template = confs.get('template', '{status.sender}: {time} {status.data[level]} {status.data[message]}')

    def run(self):
        while True:
            try:
                self.run_()
            except Exception as e:
                print(traceback.format_exc())

    def onmessage(self, message):
        self.write(message)
        
        message.data['sender'] = message.sender
        message.sender = self.filtername
        self.Q.put(message)

    def write(self, message):
        now = datetime.datetime.now()
        line = self.template.format(status=message, time=now)
        with open(self.getfile(), 'a') as fp:
            print(line, file=fp)

    def getfile(self):
        return self.logdir + '/' + self.logfile
