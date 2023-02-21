"""
Auto-replay chat robot abstract class
"""
from common.data import Reply, Context


class Bot(object):
    def reply(self, context: Context) -> Reply:
        """
        bot auto-reply
        :param context: context info
        :return: Reply
        """
        raise NotImplementedError
