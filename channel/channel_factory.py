"""
channel factory
"""


def create_channel(channel_type):
    """
    create a channel instance
    :param channel_type: channel type code
    :return: channel instance
    """
    if channel_type == 'dt':
        from channel.dingtalk.dingtalk_channel import DingTalkChannel
        return DingTalkChannel()
    raise RuntimeError
