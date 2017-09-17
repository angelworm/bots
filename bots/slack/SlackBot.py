
import requests

from ..common import Status

class SlackMessage:
    def __init__(self, channel, text, issuer=None):
        self.channel = channel
        self.text = text
        self.issuer = issuer
        
    def toquery(self, token):
        data = {
            'text': self.text,
            'channel': self.channel,
            'token': token,
            'as_user': True
        }

        if self.issuer is not None:
            isq = {}
            for key in ['username', 'icon_url', 'icon_emoji']:
                if key in self.issuer:
                    isq[key] = self.issuer[key]

            data.update(isq)
            data['as_user'] = len(isq) == 0

        return data
            
class SlackBot:
    def __init__(self, confs):
        self.token = confs['token']
        self.filtername = confs['filtername']
        self.defaultissuer = confs.get('defaultissuer', None)

    def run(self, iQ, oQ):
        while True:
            message = iQ.get()
            self.onmessage(message)

    def onmessage(self, message):
        data = message.data

        channel = data['channel']
        text = data['text']
        issuer = data.get('issuer', self.defaultissuer)

        self.postslack(SlackMessage(channel, text, issuer))
        
    def postslack(self, smsg):
        return requests.post('https://slack.com/api/chat.postMessage', smsg.toquery(self.token))
        
