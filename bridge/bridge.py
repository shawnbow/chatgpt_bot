from bot import create_bot
from common.data import Reply


class Bridge(object):
    def __init__(self):
        pass

    def fetch_reply(self, content, context) -> Reply:
        return create_bot('openai').reply(content, context)
