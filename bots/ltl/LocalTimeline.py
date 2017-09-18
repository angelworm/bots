# -*- coding: utf-8 -*-

from mastodon import Mastodon
from mastodon.streaming import StreamListener, MalformedEventError
from collections import OrderedDict

from ..common import Status, FilterBase

class LocalTimelineStreamListener(StreamListener):
    def __init__(self, confs, maxcahcesize, filtername, Q):
        self.confs = confs
        self.Q = Q
        self.cache = OrderedDict()
        self.maxcachesize = maxcahcesize if maxcahcesize is not None else 10000
        self.filtername = filtername if filtername is not None else 'mastodon-ltl'

    def on_update(self, status):
        self.cache[status['id']] = status
        cap = len(self.cache) - self.maxcachesize
        for i in range(cap):
            self.cache.popitem(last = False)

        message = self.gen_message_('ltl.update', status)
        self.Q.put(message)

    def on_notification(self, notification):
        pass

    def on_delete(self, status_id):
        message = self.gen_message_('ltl.delete', {
            'id': int(status_id)
        })
        self.Q.put(message)

        if status_id in self.cache:
            found = self.cache[status_id]
            message = self.gen_message_('ltl.delete.found', found)
            self.Q.put(message)

    def handle_heartbeat(self):
        pass

    def gen_message_(self, type, data):
        return Status(self.filtername, type, data)

class LocalTimeline(FilterBase):

    def __init__(self, confs):
        super().__init__(confs['filtername'])
        self.client_id = confs['client_id']
        self.client_secret = confs['client_secret']
        self.access_token = confs['access_token']
        self.host = confs['host']
        self.maxcahcesize = confs.get('maxcachesize', None)
        self.confs = confs

    def run_(self):
        self.mastodon = Mastodon(
            client_id = self.client_id,
            client_secret = self.client_secret,
            access_token = self.access_token,
            api_base_url = self.host)

        self.listener = LocalTimelineStreamListener(self.confs, self.maxcahcesize, self.filtername, self.Q)
        self.mastodon.local_stream(self.listener, async=False)
