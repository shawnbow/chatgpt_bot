"""
Auto-replay chat robot abstract class
"""
from common.data import Reply, Context, Query


class Bot(object):
    def reply(self, query: Query, context: Context) -> Reply:
        """
        bot auto-reply
        :param query: query info
        :param context: context info
        :return: Reply
        """
        raise NotImplementedError
