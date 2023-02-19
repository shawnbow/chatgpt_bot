# encoding:utf-8

"""
dingtalk channel
"""
import json
from concurrent.futures import ThreadPoolExecutor
from config import Config
from common.data import Reply
from common.log import logger
from channels.channel import Channel
from .service import DingTalk


class DingTalkChannel(Channel):

    def startup(self):
        DingTalk.register_handlers('msg_handler', lambda msg: self.handle(msg))
        DingTalk.run()

    def handle(self, msg):
        logger.debug(f'[DT] received msg={json.dumps(msg, ensure_ascii=False)}')

        content = msg.get('text', {}).get('content', None)
        content = content.strip() if content else None
        if not content:
            return

        context = {
            'user_id': msg.get('senderId', None),
            'user_name': msg.get('senderNick', None),

            'session_webhook': msg.get('sessionWebhook', None),
            'session_webhook_expired_time': msg.get('sessionWebhookExpiredTime', None),
            'sender_staff_id': msg.get('senderStaffId', None),
            'conversation_id': msg.get('conversationId', None),
            'conversation_title': msg.get('conversationTitle', None),
        }

        try:
            reply = super().fetch_reply(content, context)
        except Exception as e:
            logger.exception(e)
            reply = Reply(by='dt', type='TEXT', result='exception', msg='出错了, 再发送一次')

        try:
            self.send(reply, context)
        except Exception as e:
            logger.exception(e)

    def send(self, reply: Reply, context):
        sender = DingTalk.sender(context)

        if not sender:
            logger.error('[DT] sender is null!')
            return

        if reply.type == 'IMAGE':
            sender.send_image(reply.msg)
        else:
            sender.send_text(reply.msg)

        logger.debug(f'[DT] send reply(by={reply.by}, type={reply.type}, result={reply.result}, msg={reply.msg}).')

