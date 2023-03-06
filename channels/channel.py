"""
Message sending channel abstract class
"""

from bridge.bridge import Bridge
from common.data import Reply, Context, Query


class Channel(object):
    def startup(self):
        """
        init channel
        """
        raise NotImplementedError

    def fetch_reply(self, query: Query, context: Context) -> Reply:
        return Bridge().fetch_reply(query, context)
