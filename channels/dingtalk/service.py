from pprint import pprint
import hmac
import hashlib
import base64
import json
import arrow
from typing import Dict, Callable, Optional

import tornado.ioloop
import tornado.web
import asyncio
from tornado.concurrent import run_on_executor
from dingtalkchatbot.chatbot import DingtalkChatbot
from concurrent.futures import ThreadPoolExecutor

from config import Config
from common.data import Context
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
        handler = self.__class__.handlers['msg_handler']
        self.executor.submit(handler, data)
        return self.finish({'errcode': 0, 'msg': 'received'})

    async def sleep_asyncio(self):
        await asyncio.sleep(1)
        return arrow.now().format()

    async def get(self):
        logger.debug(f'begin get {arrow.now().format()}')
        _now = await self.sleep_asyncio()
        logger.debug(f'done get {_now}')

        self.set_status(200)
        return self.finish({'errcode': 0, 'msg': _now})


class DingTalk:
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
    def sender(context: Context) -> Optional[DingtalkChatbot]:
        session_webhook = context.extra['session_webhook']
        expired_time = context.extra['session_webhook_expired_time']
        group_id = context.extra['conversation_id']
        _now = int(arrow.now().float_timestamp * 1000)

        if session_webhook and expired_time and _now < expired_time:
            # session webhook not expired
            return DingtalkChatbot(session_webhook)

        if group_id:
            # use group bot webhook config
            webhook = Config.dt('webhooks').get(group_id, {})
            webhook_token = webhook.get('webhook_token', None)
            webhook_secret = webhook.get('webhook_secret', None)
            if webhook_token:
                return DingtalkChatbot(webhook_token, secret=webhook_secret)

        return None


if __name__ == '__main__':
    DingTalk.run()
