"""
channel factory
"""


def create_bot(channel_name):
    """
    create a channel instance
    :param channel_name: channel type code
    :return: channel instance
    """
    if channel_name == 'openai':
        from bot.openai.engine import OpenAIBot
        return OpenAIBot()
    raise RuntimeError
