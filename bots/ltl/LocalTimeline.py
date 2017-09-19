# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
from mastodon import Mastodon
from mastodon.streaming import StreamListener, MalformedEventError
from collections import OrderedDict
import redis
import pickle

from ..common import Status, FilterBase

def flat_el(el):
    if el.tag == 'br':
        return '\n'

    ret = el.text if el.text is not None else ''
    for x in el:
        ret += flat_el(x)
        ret += x.tail if x.tail is not None else ''
    return ret

def flatten_message(status):
    ret = dict(status)
    try:
        text = '<div>{}</div>'.format(status['content'])
        el = ET.fromstring(text)

        ps = list(flat_el(x) for x in el)

        ret['content'] = '\n\n'.join(ps)
    except ET.ParseError:
        print(status['content'])
    return ret

class LocalTimelineStreamListener(StreamListener):
    def __init__(self, confs, maxcahcesize, filtername, Q):
        self.confs = confs
        self.Q = Q
        self.filtername = filtername if filtername is not None else 'mastodon-ltl'
        self.cache = redis.StrictRedis()

    def put_cache_(self, status):
        key = 'ltl:{}:{}'.format(self.filtername, status['id'])
        self.cache.set(key, pickle.dumps(status), ex=60 * 60 * 6)

    def get_cache(self, status_id):
        key = 'ltl:{}:{}'.format(self.filtername, status_id)
        status = self.cache.get(key)
        return pickle.loads(status) if status is not None else None

    def on_update(self, status):
        status = flatten_message(status)

        self.put_cache_(status)

        message = self.gen_message_('ltl.update', status)
        self.Q.put(message)

    def on_notification(self, notification):
        pass

    def on_delete(self, status_id):
        message = self.gen_message_('ltl.delete', {
            'id': int(status_id)
        })
        self.Q.put(message)

        found = self.get_cache(status_id)
        if found is not None:
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
