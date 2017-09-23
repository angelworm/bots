
import unittest
import tempfile
import os
import os.path
import queue

from bots.logger import FileLogger
from bots.common import Status

class FileLoggerTest(unittest.TestCase):
    def setUp(self):
        self.logdir = tempfile.mkdtemp()
        self.logfile = 'test.log'

    def tearDown(self):
        for root, dirs, files in os.walk(self.logdir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        
    def test_output(self):
        Q = queue.Queue()

        f = FileLogger({
            'filtername': 'test',
            'dir': self.logdir,
            'file': self.logfile
        })
        f.Q = Q

        status = Status('sender', 'sys.log', {
            'level': 'INFO',
            'message': 'logmessage1'
        })
        f.onmessage(status)

        ret = Q.get(0)
        self.assertTrue(Q.empty())
        self.assertEqual(ret.sender, 'test')
        self.assertEqual(ret.type, 'sys.log')
        self.assertEqual(ret.data, {
            'level': 'INFO',
            'message': 'logmessage1',
            'sender': 'sender'
        })

        path = self.logdir + '/' + self.logfile
        self.assertTrue(os.path.exists(path))
        with open(path, 'r') as fp:
            contents = fp.read()
            self.assertTrue('INFO' in contents)
            self.assertTrue('logmessage1' in contents)
            self.assertTrue('sender' in contents)

if __name__ == '__main__':
    unittest.main()
