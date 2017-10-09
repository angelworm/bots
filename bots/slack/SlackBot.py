
import requests

from ..common import Status, FilterBase

class SlackBot(FilterBase):
    def __init__(self, confs):
        super().__init__(confs['filtername'])
        self.token = confs['token']
        self.defaultissuer = confs.get('defaultissuer', None)
        self.notfound = []

    def onmessage(self, message):
        data = message.data
        query = self.makemessage(data)

        ret = self.postslack(query)
        try:
            rj = ret.json()
            if not rj.get('ok', True):
                if rj.get('error', '') == 'channel_not_found':
                    ch = query['channel']
                    if ch not in self.notfound:
                        self.notfound.append(ch)
                        self.log('channel not found {}'.format(ch))
        except ValueError as e:
            self.log(ret.text)

    def makemessage(self, data):
        channel = data['channel']
        text = data['text']
        issuer = data.get('issuer', self.defaultissuer)

        return self.toquery(channel, text, issuer)

    def normalize_channel(self, txt):
        ret = ''
        if txt is None:
            pass
        elif '-' in txt:
            chs = txt.split('-', 1)
            main = chs[0]
            sub = chs[1]

            ret = main[:10] + '-' + sub
            ret = ret[:21]
        else:
            ret = txt[:21]

        replacements = [' ', '.', '。', '、', '「', '」', '【', '】', '\'']
        for r in replacements:
            ret = ret.replace(r, '_')
        return ret

    def toquery(self, channel, text, issuer):
        data = {
            'text': text,
            'channel': self.normalize_channel(channel),
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
        return requests.post('https://slack.com/api/chat.postMessage', query, timeout=10)
