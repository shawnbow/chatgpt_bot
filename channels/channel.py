"""
Message sending channel abstract class
"""

from bridge.bridge import Bridge
from common.data import Reply, Context


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
        :param reply: reply by bot
        :param context: context info
        :return: 
        """
        raise NotImplementedError

    def fetch_reply(self, context: Context) -> Reply:
        return Bridge().fetch_reply(context)
