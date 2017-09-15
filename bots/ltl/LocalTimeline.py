# -*- coding: utf-8 -*-

from mastodon import Mastodon
from mastodon.streaming import StreamListener, MalformedEventError

from ..common import Status

class LocalTimelineStreamListener(StreamListener):
    def __init__(self, confs, maxcahcesize, filtername, Q):
        self.confs = confs
        self.Q = Q
        self.cache = []
        self.maxcachesize = maxcahcesize if maxcahcesize is not None else 10000
        self.filtername = filtername if filtername is not None else 'mastodon-ltl'

    def on_update(self, status):
        self.cache.append(status)
        self.cache = self.cache[:self.maxcachesize]
        
        message = self.gen_message_('ltl_update', status)
        self.Q.put(message)

    def on_notification(self, notification):
        pass
        
    def on_delete(self, status_id):
        found = {
            'id': int(status_id)
        }
        for s in self.cache:
            if s['id'] == status_id:
                found = s
        
        message = self.gen_message_('ltl_delete', found)
        self.Q.put(message)

    def handle_heartbeat(self):
        pass

    def gen_message_(self, type, data):
        return Status(self.filtername, type, data)
    
class LocalTimeline:

    def __init__(self, confs):
        self.client_id = confs['client_id']
        self.client_secret = confs['client_secret']
        self.access_token = confs['access_token']
        self.host = confs['host']
        self.filtername = confs['filtername']
        self.maxcahcesize = confs.get('maxcachesize', None)
        self.confs = confs

    def run(self, iQ, oQ):
        self.Q = oQ
        self.mastodon = Mastodon(
            client_id = self.client_id,
            client_secret = self.client_secret,
            access_token = self.access_token,
            api_base_url = self.host)

        self.listener = LocalTimelineStreamListener(self.confs, self.maxcahcesize, self.filtername, self.Q)
        self.mastodon.local_stream(self.listener, async=True)
