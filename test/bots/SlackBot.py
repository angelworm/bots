
import unittest

from bots.slack.SlackBot import SlackBot
from bots.common import Status

class SlackBotTest(unittest.TestCase):
    def test_makemessage(self):
        status1 = {
            'channel': '#ch1',
            'text': 'some text'
        }
        status2 = {
            'channel': '#ch1',
            'text': 'some text',
            'issuer': {
                'username': 'bot user',
                'icon_url': 'http://'
            }
        }
        defaultissuer = {
            'username': 'defaultuser',
            'icon_url': 'http://default'
        }

        bot = SlackBot({
            'token': 'test-token-XXX',
            'filtername': 'slackbot-1'
        })
        
        ret = bot.makemessage(status1)

        self.assertEqual(ret, {
            'channel': '#ch1',
            'text': 'some text',
            'token': 'test-token-XXX',
            'as_user': True
        })
        
        ret = bot.makemessage(status2)

        self.assertEqual(ret, {
            'channel': '#ch1',
            'text': 'some text',
            'token': 'test-token-XXX',
            'as_user': False,
            'username': 'bot user',
            'icon_url': 'http://'
        })
        
        bot = SlackBot({
            'token': 'test-token-XXX',
            'filtername': 'slackbot-1',
            'defaultissuer': defaultissuer
        })
        
        ret = bot.makemessage(status1)

        self.assertEqual(ret, {
            'channel': '#ch1',
            'text': 'some text',
            'token': 'test-token-XXX',
            'as_user': False,
            'username': defaultissuer['username'],
            'icon_url': defaultissuer['icon_url']
        })
        
        ret = bot.makemessage(status2)

        self.assertEqual(ret, {
            'channel': '#ch1',
            'text': 'some text',
            'token': 'test-token-XXX',
            'as_user': False,
            'username': 'bot user',
            'icon_url': 'http://'
        })
