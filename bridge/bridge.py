from bot import create_bot
from common.data import Reply, Context


class Bridge(object):
    def __init__(self):
        pass

    def fetch_reply(self, context: Context) -> Reply:
        return create_bot('openai').reply(context)
