from pprint import pprint
import hmac
import hashlib
import base64
import json

import config

import tornado.ioloop
import tornado.web

class DingTalkRobot(tornado.web.RequestHandler):
    app_secret = config.conf()['dingtalk']['app_secret']

    def check_sig(self, timestamp):
        app_secret_enc = self.app_secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.app_secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(app_secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign

    async def post(self):
        timestamp = self.request.headers.get('timestamp', None)
        sign = self.request.headers.get('sign', None)
        if sign != self.check_sig(timestamp):
            return self.finish({"errcode": 1, "msg": "签名有误"})
        data = json.loads(self.request.body)
        pprint(data)
        text = data['text']["content"]
        # atUsers = data.get("atUsers", None)
        # uid = data.get("senderStaffId", None)
        return self.finish({"errcode": 0, "msg": text})


def main():
    app = tornado.web.Application([(r"/", DingTalkRobot)])
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
