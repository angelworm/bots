
from bots.converter import Converter
from bots.common import Status

import unittest
import queue

class ConverterTest(unittest.TestCase):
    def test_onmessage_type(self):
        filtername = 'filter1'
        statustype = 'message.post'
        
        bot = Converter({
            'filtername': 'converter1'
        })
        bot.Q = queue.Queue()

        status = Status(filtername, statustype, {})
        
        bot.onmessage(status)
        ret = bot.Q.get(0)
        
        self.assertEqual(ret.sender, 'converter1')
        self.assertEqual(ret.type, statustype)
        self.assertTrue(bot.Q.empty())
        
        bot = Converter({
            'filtername': 'converter1',
            'type': '{sender}'
        })
        bot.Q = queue.Queue()

        status = Status(filtername, statustype, {})
        
        bot.onmessage(status)
        ret = bot.Q.get(0)
        
        self.assertEqual(ret.sender, 'converter1')
        self.assertEqual(ret.type, filtername)
        self.assertTrue(bot.Q.empty())
        
        bot = Converter({
            'filtername': 'converter1',
            'type': '{data[id]}'
        })
        bot.Q = queue.Queue()

        status = Status(filtername, statustype, {'id': 'id1'})
        
        bot.onmessage(status)
        ret = bot.Q.get(0)
        
        self.assertEqual(ret.sender, 'converter1')
        self.assertEqual(ret.type, 'id1')
        self.assertTrue(bot.Q.empty())
        
        bot = Converter({
            'filtername': 'converter1',
            'type': '{data[id][id]}'
        })
        bot.Q = queue.Queue()

        status = Status(filtername, statustype, {'id': {'id': 'id1'}})
        
        bot.onmessage(status)
        ret = bot.Q.get(0)
        
        self.assertEqual(ret.sender, 'converter1')
        self.assertEqual(ret.type, 'id1')
        self.assertTrue(bot.Q.empty())
        
    def test_onmessage_data(self):
        filtername = 'filter1'
        statustype = 'message.post'
        
        bot = Converter({
            'filtername': 'converter1'
        })
        bot.Q = queue.Queue()
        status = Status(filtername, statustype, {})
        
        bot.onmessage(status)
        ret = bot.Q.get(0)
        
        self.assertEqual(ret.data, {})
        self.assertTrue(bot.Q.empty())
        
        bot = Converter({
            'filtername': 'converter1',
            'data': {
                'sender': '{sender}',
                'type': '{type}',
                'data': {
                    'level1': '{data[text1]}',
                    'nest1': {
                        'level2': '{{{data[text2]}}}'
                    }
                }
            }
        })
        bot.Q = queue.Queue()
        status = Status(filtername, statustype, {
            'text1': 'tx1',
            'text2': 'tx2'
        })
        
        bot.onmessage(status)
        ret = bot.Q.get(0)
        
        self.assertEqual(ret.data, {
            'sender': filtername,
            'type': statustype,
            'data': {
                'level1': 'tx1',
                'nest1': {
                    'level2': '{tx2}'
                }
            }
        })
        self.assertTrue(bot.Q.empty())
