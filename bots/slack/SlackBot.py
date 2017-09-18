
import requests

from ..common import Status, FilterBase

class SlackBot(FilterBase):
    def __init__(self, confs):
        super().__init__(confs['filtername'])
        self.token = confs['token']
        self.defaultissuer = confs.get('defaultissuer', None)

    def run_(self):
        while True:
            message = self.iQ.get()
            self.onmessage(message)

    def onmessage(self, message):
        data = message.data
        query = self.makemessage(data)
        self.postslack(query)

    def makemessage(self, data):
        channel = data['channel']
        text = data['text']
        issuer = data.get('issuer', self.defaultissuer)

        return self.toquery(channel, text, issuer)

    def toquery(self, channel, text, issuer):
        data = {
            'text': text,
            'channel': channel,
            'token': self.token,
            'as_user': True
        }

        if issuer is not None:
            isq = {}
            for key in ['username', 'icon_url', 'icon_emoji']:
                if key in issuer:
                    isq[key] = issuer[key]

            data.update(isq)
            data['as_user'] = len(isq) == 0

        return data

    def postslack(self, query):
        return requests.post('https://slack.com/api/chat.postMessage', query)
