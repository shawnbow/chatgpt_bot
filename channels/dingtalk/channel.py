# encoding:utf-8

"""
dingtalk channel
"""
import json
import arrow
from concurrent.futures import ThreadPoolExecutor
from config import Config
from common.utils import IntEncoder
from common.data import Reply, Context, Query
from common.log import logger
from channels.channel import Channel
from .service import DingTalk


class DingTalkChannel(Channel):

    def startup(self):
        DingTalk.register_handlers('msg_handler', lambda msg: self.handle(msg))
        DingTalk.run()

    def handle(self, msg):
        logger.debug(f'[DT] received msg={json.dumps(msg, ensure_ascii=False)}')

        query = Query(
            msg_id=msg.get('msgId', IntEncoder.encode_now('msg')),
            msg_type=msg.get('msgtype', 'text'),
            msg=msg.get('text', {}).get('content', '').strip(),  # TODO: picture message
            created_at=msg.get('createAt', 0)
        )

        context = Context(
            user_id=msg.get('senderId', 'ding_user'),
            user_name=msg.get('senderNick', 'ding_user'),
            group_id=msg.get('conversationId', 'ding_group'),
            group_name=msg.get('conversationTitle', 'ding_group'),
            is_group_chat=(True if msg.get('conversationType', '1') == '2' else False),
            platform='DingTalk',
            extra=msg
        )

        try:
            reply = super().fetch_reply(query, context)
        except Exception as e:
            logger.exception(e)
            reply = Reply(by='dt', type='TEXT', result='error', msg='出错了, 再发送一次')

        try:
            self.send(reply, context)
        except Exception as e:
            logger.exception(e)

    def send(self, reply, context):
        sender = DingTalk.sender(context)

        if not sender:
            logger.error('[DT] sender is null!')
            return

        if reply.type == 'IMAGE':
            sender.send_markdown(
                title='GPT',
                text=f'#### By DALL·E Model\n'
                     f'> ![]({reply.msg})\n'
                     f'> ###### {context.extra.get("text", {}).get("content", "")}\n')
        else:
            sender.send_text(reply.msg)

        logger.debug(f'[DT] send reply(by={reply.by}, type={reply.type}, result={reply.result}, msg={reply.msg}).')
