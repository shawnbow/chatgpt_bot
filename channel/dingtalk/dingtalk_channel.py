# encoding:utf-8

"""
dingtalk channel
"""
import json
from channel.channel import Channel
from concurrent.futures import ThreadPoolExecutor
from common.log import logger
from config import conf
import dingtalk.bot


class DingTalkChannel(Channel):
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=8)

    def startup(self):
        dingtalk.bot.MessageHandler.register_handlers('handle_reply', lambda msg: self.handle(msg))
        dingtalk.bot.run()

    def handle(self, msg):
        content = msg.get('text', {}).get('content', None)
        content = content.strip() if content else None
        if not content:
            return

        session = {
            'conversation_id': msg.get('conversationId', None),
            'conversation_title': msg.get('conversationTitle', None),
            'sender_id': msg.get('senderId', None),
            'sender_nick': msg.get('senderNick', None),
            'sender_staff_id': msg.get('senderId', None),
            'session_webhook': msg.get('sessionWebhook', None),
            'session_webhook_expired_time': msg.get('sessionWebhookExpiredTime', None),
        }
        img_match_prefix = self.check_prefix(content, conf().get('image_create_prefix'))
        if img_match_prefix:
            content = content.split(img_match_prefix, 1)[1].strip()
            self.executor.submit(self._do_send_img, content, session)
        else:
            self.executor.submit(self._do_send, content, session)

    def send(self, msg, receiver):
        pass

    def _do_send(self, query, session):
        try:
            if not query:
                return
            context = dict()
            context['type'] = 'TEXT'
            context['from_user_id'] = session['sender_id']
            reply_text = super().build_reply_content(query, context)
            if reply_text:
                logger.info(f'[DT] sendMsg={reply_text}, receiver={session["sender_id"]}')
                dingtalk.bot.sender(session['session_webhook'], session['session_webhook_expired_time']).send_text(reply_text)
        except Exception as e:
            logger.exception(e)

    def _do_send_img(self, query, session):
        try:
            if not query:
                return
            context = dict()
            context['type'] = 'IMAGE_CREATE'
            context['from_user_id'] = session['sender_id']
            img_url = super().build_reply_content(query, context)
            if img_url:
                logger.info(f'[DT] sendImage={img_url}, receiver={session["sender_id"]}')
                dingtalk.bot.sender(session['session_webhook'], session['session_webhook_expired_time']).send_image(img_url)
        except Exception as e:
            logger.exception(e)

    @classmethod
    def check_prefix(cls, content, prefix_list):
        for prefix in prefix_list:
            if content.startswith(prefix):
                return prefix
        return None

    @classmethod
    def check_contain(cls, content, keyword_list):
        if not keyword_list:
            return None
        for ky in keyword_list:
            if content.find(ky) != -1:
                return True
        return None
