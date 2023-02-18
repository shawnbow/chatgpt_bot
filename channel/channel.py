"""
Message sending channel abstract class
"""

from bridge.bridge import Bridge
from common.data import Reply


class Channel(object):
    def startup(self):
        """
        init channel
        """
        raise NotImplementedError

    def handle(self, msg):
        """
        process received message
        :param msg: message object
        """
        raise NotImplementedError

    def send(self, reply: Reply, context):
        """
        send message to user
        :param reply: message content
        :param context: context
        :return: 
        """
        raise NotImplementedError

    def fetch_reply(self, content, context=None) -> Reply:
        return Bridge().fetch_reply(content, context)
