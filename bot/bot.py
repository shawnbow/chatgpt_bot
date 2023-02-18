"""
Auto-replay chat robot abstract class
"""
from common.data import Reply


class Bot(object):
    def reply(self, content, context=None) -> Reply:
        """
        bot auto-reply content
        :param content: received message
        :param context: context info
        :return: Reply
        """
        raise NotImplementedError
