# encoding:utf-8

"""
dingtalk channel
"""
import json
from channel.channel import Channel
from concurrent.futures import ThreadPoolExecutor
from common.log import logger
from config import conf
import requests
import dingtalk.bot

thread_pool = ThreadPoolExecutor(max_workers=8)


class DingTalkChannel(Channel):
    def __init__(self):
        pass

    def startup(self):
        dingtalk.bot.register_msg_handler(lambda msg: self.handle(msg))
        dingtalk.bot.run()

    def handle(self, msg):
        logger.debug('[DT]receive msg: ' + json.dumps(msg, ensure_ascii=False))
        group_name = msg.get('conversationTitle', None)
        sender_staff_id = msg.get('senderStaffId', None)
        sender_id = msg.get('senderId', None)
        sender_nick = msg.get('senderNick', None)
        content = msg.get('text', {}).get('content', None)
        session_web_hook = msg.get('sessionWebhook', None)
        session_webhook_expired_time = msg.get('sessionWebhookExpiredTime', None)

        img_match_prefix = self.check_prefix(content, conf().get('image_create_prefix'))
        if img_match_prefix:
            content = content.split(img_match_prefix, 1)[1].strip()
            thread_pool.submit(self._do_send_img, content, sender_id)
        else:
            thread_pool.submit(self._do_send, content, sender_id)

    def send(self, msg, receiver):
        pass

    def _do_send(self, query, reply_user_id):
        try:
            if not query:
                return
            context = dict()
            context['from_user_id'] = reply_user_id
            reply_text = super().build_reply_content(query, context)
            if reply_text:
                logger.info(f'[DT] sendMsg={reply_text}, receiver={reply_user_id}')
                dingtalk.bot.default_sender.send_text(reply_text)
        except Exception as e:
            logger.exception(e)

    def _do_send_img(self, query, reply_user_id):
        try:
            if not query:
                return
            context = dict()
            context['type'] = 'IMAGE_CREATE'
            img_url = super().build_reply_content(query, context)
            if img_url:
                logger.info(f'[DT] sendImage={img_url}, receiver={reply_user_id}')
                dingtalk.bot.default_sender.send_image(img_url)
        except Exception as e:
            logger.exception(e)

    def check_prefix(self, content, prefix_list):
        for prefix in prefix_list:
            if content.startswith(prefix):
                return prefix
        return None

    def check_contain(self, content, keyword_list):
        if not keyword_list:
            return None
        for ky in keyword_list:
            if content.find(ky) != -1:
                return True
        return None
