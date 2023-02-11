from pprint import pprint
import hmac
import hashlib
import base64
import json

from config import conf

import tornado.ioloop
import tornado.web
from dingtalkchatbot.chatbot import DingtalkChatbot

class MessageHandler(tornado.web.RequestHandler):
    msg_handler = None

    def check_sig(self, timestamp):
        app_secret = conf()['dingtalk']['app_secret']
        app_secret_enc = app_secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, app_secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(app_secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign

    def post(self):
        timestamp = self.request.headers.get('timestamp', None)
        sign = self.request.headers.get('sign', None)
        if timestamp is None or sign is None:
            return self.finish({'errcode': 100, 'msg': 'invalid request'})
        if sign != self.check_sig(timestamp):
            return self.finish({'errcode': 1, 'msg': 'error sign'})
        data = json.loads(self.request.body)
        # text = data['text']['content']
        # sessionWebhook = data['sessionWebhook']
        # atUsers = data.get("atUsers", None)
        # uid = data.get("senderStaffId", None)
        if self.__class__.msg_handler:
            self.__class__.msg_handler(data)
        return self.finish({'errcode': 0, 'msg': 'received'})

    def get(self):
        self.set_status(200)
        return self.finish({'errcode': 0, 'msg': 'hello'})


default_sender = DingtalkChatbot(conf()['dingtalk']['webhook_token'], secret=conf()['dingtalk']['webhook_secret'])


def register_msg_handler(handler):
    MessageHandler.msg_handler = handler


def run():
    url_map = [
        (r'%s' % conf()['dingtalk']['receiver_url'], MessageHandler),
    ]
    app = tornado.web.Application(url_map)
    app.listen(conf()['dingtalk']['receiver_port'])
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    run()
