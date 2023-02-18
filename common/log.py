import os
import sys
from pprint import pprint
from datetime import datetime
from config import Config


class Logger:
    def __init__(self, project: str, rm_stderr: bool = False):
        from loguru import logger

        self.log_dir = f'{Config.log_path()}/{project}'
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        self.debug_path = f'{self.log_dir}/debug.log'
        self.info_path = f'{self.log_dir}/info.log'
        self.error_path = f'{self.log_dir}/error.log'
        if rm_stderr:
            logger.remove(0)
        # ERROR > INFO > DEBUG, 高级别的log可以打印到低级别的文件/流中, 除非低级别设置了过滤器
        # logger.add(
        #     sys.stderr,
        #     format='{time}|{function}:<{module}>:{line}|{message}',
        #     level='TRACE')
        logger.add(
            self.debug_path,
            format='{time}|{level}|{function}:<{module}>:{line}|{message}',
            level='DEBUG')
        logger.add(
            self.info_path,
            format='{time}|{level}|{function}:<{module}>:{line}|{message}',
            level='INFO')
        logger.add(
            self.error_path,
            format='{time}|{level}|{function}:<{module}>:{line}|{message}',
            level='ERROR')
        self.loguru = logger
        self.info = logger.info
        self.debug = logger.debug
        self.warn = logger.warning
        self.error = logger.error
        self.exception = logger.exception

        # 以下打印不记录到文件
        self.print = print
        self.wprint = lambda *args, **kwargs: print(f'{datetime.now().isoformat()[:-3]}:', *args, **kwargs)
        self.pprint = pprint


# 日志句柄
logger = Logger('chatgpt')

if __name__ == '__main__':
    pass
