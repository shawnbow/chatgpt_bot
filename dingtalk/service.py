from pprint import pprint
import hmac
import hashlib
import base64
import json
import arrow
from typing import Dict, Callable

import tornado.ioloop
import tornado.web
import asyncio
from tornado.concurrent import run_on_executor
from dingtalkchatbot.chatbot import DingtalkChatbot
from concurrent.futures import ThreadPoolExecutor

from config import Config
from common.utils import BoostDict
from common.log import logger


class MessageHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=8)

    app_secret = Config.dt('app_secret')

    handlers: Dict[str, Callable] = BoostDict(lambda k: (lambda data: logger.error(f'empty callback: key={k} data={data}')))

    @classmethod
    def check_sig(cls, timestamp):
        app_secret_enc = cls.app_secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, cls.app_secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(app_secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign

    async def post(self):
        timestamp = self.request.headers.get('timestamp', None)
        sign = self.request.headers.get('sign', None)
        if timestamp is None or sign is None:
            logger.error('[DT] invalid request')
            return self.finish({'errcode': 100, 'msg': 'invalid request'})
        if sign != self.check_sig(timestamp):
            logger.error('[DT] error sign')
            return self.finish({'errcode': 1, 'msg': 'error sign'})

        data = json.loads(self.request.body)
        logger.debug('[DT] body=' + json.dumps(data, ensure_ascii=False))

        handler = self.__class__.handlers['msg_handler']
        self.executor.submit(handler, data)
        return self.finish({'errcode': 0, 'msg': 'received'})

    async def sleep_asyncio(self):
        await asyncio.sleep(5)
        return arrow.now().format()

    async def get(self):
        logger.info(f'begin get {arrow.now().format()}')
        _now = await self.sleep_asyncio()
        logger.info(f'done get {_now}')

        self.set_status(200)
        return self.finish({'errcode': 0, 'msg': _now})


class Service:
    @staticmethod
    def register_handlers(key, callback):
        MessageHandler.handlers[key] = callback

    @staticmethod
    def run():
        url_map = [
            (r'%s' % Config.dt('server_url'), MessageHandler),
        ]
        app = tornado.web.Application(url_map)
        app.listen(Config.dt('server_port'))
        tornado.ioloop.IOLoop.current().start()

    @staticmethod
    def sender(session_webhook=None, session_webhook_expired_time=None) -> DingtalkChatbot:
        if session_webhook and session_webhook_expired_time and session_webhook_expired_time > arrow.now().int_timestamp * 1000:
            return DingtalkChatbot(session_webhook)
        else:
            return DingtalkChatbot(Config.dt('webhook_token'), secret=Config.dt('webhook_secret'))


if __name__ == '__main__':
    Service.run()
