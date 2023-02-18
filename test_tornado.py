from pprint import pprint
import hmac
import hashlib
import base64
import json
import arrow
from typing import Dict, Callable
from collections import defaultdict

from config import Config
import time
import tornado.ioloop
import tornado.web
import asyncio
from tornado.concurrent import run_on_executor
from dingtalkchatbot.chatbot import DingtalkChatbot
from concurrent.futures import ThreadPoolExecutor
from common.utils import BoostDict


class MessageHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=8)

    handler = None

    @run_on_executor
    def sleep_thread_pool(self):
        time.sleep(5)
        return arrow.now().format()

    async def sleep_asyncio(self):
        await asyncio.sleep(5)
        return arrow.now().format()

    async def get(self):
        print(f'begin get {arrow.now().format()}')
        # _now = await self.sleep_thread_pool()
        _now = await self.sleep_asyncio()
        print(f'done get {_now}')

        self.__class__.handler(_now)

        self.set_status(200)
        return self.finish({'errcode': 0, 'msg': _now})


def run():
    url_map = [
        (r'%s' % Config.dt('server_url'), MessageHandler),
    ]
    app = tornado.web.Application(url_map)
    app.listen(Config.dt('server_port'))
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    run()
