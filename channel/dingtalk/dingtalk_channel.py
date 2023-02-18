# encoding:utf-8

"""
dingtalk channel
"""
import json
from config import Config
from common.data import Reply
from common.log import logger
from channel.channel import Channel
from concurrent.futures import ThreadPoolExecutor
from dingtalk import dtchat


class DingTalkChannel(Channel):

    def startup(self):
        dtchat.register_handlers('msg_handler', lambda msg: self.handle(msg))
        dtchat.run()

    def handle(self, msg):
        content = msg.get('text', {}).get('content', None)
        content = content.strip() if content else None
        if not content:
            return

        context = {
            'user_id': msg.get('senderId', None),
            'user_name': msg.get('senderNick', None),
            'session_webhook': msg.get('sessionWebhook', None),
            'session_webhook_expired_time': msg.get('sessionWebhookExpiredTime', None),
            # 'sender_staff_id': msg.get('senderStaffId', None),
            # 'conversation_id': msg.get('conversationId', None),
            # 'conversation_title': msg.get('conversationTitle', None),
        }

        try:
            reply = super().fetch_reply(content, context)
        except Exception as e:
            logger.exception(e)
            reply = Reply(by='dt', type='TEXT', result='exception', msg='出错了, 再发送一次')

        self.send(reply, context)

    def send(self, reply: Reply, context):
        logger.info(f'[DT] reply by={reply.by}, type={reply.type}, result={reply.result}, msg={reply.msg} to={context["sender_id"]}')

        sender = dtchat.sender(context['session_webhook'], context['session_webhook_expired_time'])

        if reply.type == 'IMAGE':
            sender.send_image(reply.msg)
        else:
            sender.send_text(reply.msg)
