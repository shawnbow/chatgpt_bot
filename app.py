# encoding:utf-8

import config
from channel import channel_factory
from common.log import logger


if __name__ == '__main__':
    try:

        # create channel
        channel = channel_factory.create_channel("dt")

        # startup channel
        channel.startup()
        logger.info("App startup successfully!")
    except Exception as e:
        logger.error("App startup failed!")
        logger.exception(e)
