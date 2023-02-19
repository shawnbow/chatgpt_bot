# encoding:utf-8
import re
import openai
import time
from bot.bot import Bot
from config import Config
from common.log import logger
from common.data import Reply
from .session import Session


class OpenAIBot(Bot):
    def __init__(self):
        self.config = Config.openai()
        openai.api_key = self.config['api_key']

    @classmethod
    def prefix_parser(cls, content, prefix_list) -> (str, str):
        for prefix in prefix_list:
            if content.lower().startswith(prefix.lower()):
                _tmp = re.split(prefix, content, maxsplit=1, flags=re.IGNORECASE)
                if len(_tmp) > 1:
                    return prefix, _tmp[1].strip()
        return None, content

    def reply(self, content, context=None) -> Reply:
        logger.debug(f'[OPENAI] reply content={content}')
        _cmd_prefix, content = self.prefix_parser(content, self.config['cmd_prefix'])
        if _cmd_prefix:
            return self.reply_cmd(content, context)

        _image_prefix, content = self.prefix_parser(content, self.config['image_prefix'])
        if _image_prefix:
            return self.reply_img(content, context)

        _code_prefix, content = self.prefix_parser(content, self.config['code_prefix'])
        if _code_prefix:
            return self.reply_code(content, context)

        return self.reply_text(content, context)

    def reply_cmd(self, content, context):
        logger.debug(f'[OPENAI] reply_cmd content={content}')

        user_id = context['user_id']
        user_name = context['user_name']
        session = Session(user_id)

        if content.startswith('help'):
            msg = \
                '命令格式如下: \n' \
                '/help\n' \
                '/重启会话\n' \
                '/最近会话\n' \
                '/机器人性格\n' \
                '/机器人性格=你是666, 一个由OpenAI训练的大型语言模型, 你旨在回答并解决人们的任何问题，并且可以使用多种语言与人交流。\n'
            return Reply(by='openai_cmd', type='TEXT', result='done', msg=msg)
        elif content.startswith('机器人性格'):
            if content.startswith('机器人性格='):
                _tmp = content.split('=', 1)
                session.profile.set('character', _tmp[1])
                msg = f'用户名={user_name}, 用户ID={user_id}, 设置性格为: {_tmp[1]}'
                return Reply(by='openai_cmd', type='TEXT', result='done', msg=msg)
            else:
                msg = session.character
                return Reply(by='openai_cmd', type='TEXT', result='done', msg=f'当前性格是: {msg}')
        elif content.startswith('重启会话'):
            session.reset_records()
            return Reply(by='openai_cmd', type='TEXT', result='done', msg='对话已重启!')
        elif content.startswith('最近会话'):
            return Reply(
                by='openai_cmd', type='TEXT', result='done',
                msg=session.build_query(''))
        else:
            return Reply(by='openai_cmd', type='TEXT', result='error', msg='不支持该命令!')

    def reply_code(self, content, context, retry_count=0):
        logger.debug(f'[OPENAI] reply_code content={content}')

        user_id = context['user_id']
        user_name = context['user_name']

        try:
            response = openai.Completion.create(
                model=self.config['code_model'],  # 对话模型的名称
                prompt=content,
                temperature=0.9,  # 值在[0,1]之间，越大表示回复越具有不确定性
                max_tokens=self.config['max_reply_tokens'],  # 回复最大的字符数
                top_p=1,
                frequency_penalty=0.0,  # [-2,2]之间，该值越大则更倾向于产生不同的内容
                presence_penalty=0.0,  # [-2,2]之间，该值越大则更倾向于产生不同的内容
            )
            answer = response.choices[0]['text'].strip()  # replace('<|endoftext|>', '')
            logger.debug(f'[OPENAI] reply_code answer={answer}')
            return Reply(by=f'reply_code', type='TEXT', result='done', msg=answer)
        except openai.error.RateLimitError as e:
            # rate limit exception
            logger.warn(e)
            if retry_count < self.config['retry_times']:
                time.sleep(self.config['retry_interval'])
                logger.warn(f'[OPENAI] completion rate limit exceed, 第{retry_count+1}次重试')
                return self.reply_code(content, context, retry_count+1)
            else:
                return Reply(by=f'reply_code', type='TEXT', result='error', msg='提问太快啦，请休息一下再问我吧!')
        except Exception as e:
            # unknown exception
            logger.exception(e)
            return Reply(by=f'reply_code', type='TEXT', result='error', msg='OpenAI出小差了, 请再问我一次吧!')

    def reply_text(self, content, context, retry_count=0):
        logger.debug(f'[OPENAI] reply_text content={content}')

        user_id = context['user_id']
        user_name = context['user_name']
        session = Session(user_id)

        query = session.build_query(content)
        try:
            response = openai.Completion.create(
                model=self.config['text_model'],  # 对话模型的名称
                prompt=query,
                temperature=0.9,  # 值在[0,1]之间，越大表示回复越具有不确定性
                max_tokens=self.config['max_reply_tokens'],  # 回复最大的字符数
                top_p=1,
                frequency_penalty=0.0,  # [-2,2]之间，该值越大则更倾向于产生不同的内容
                presence_penalty=0.0,  # [-2,2]之间，该值越大则更倾向于产生不同的内容
                stop=["\n#\n"]
            )
            answer = response.choices[0]['text'].strip()  # replace('<|endoftext|>', '')
            logger.debug(f'[OPENAI] reply_text answer={answer}')
            session.add_record(content, answer)
            return Reply(by=f'reply_text', type='TEXT', result='done', msg=answer)
        except openai.error.RateLimitError as e:
            # rate limit exception
            logger.warn(e)
            if retry_count < self.config['retry_times']:
                time.sleep(self.config['retry_interval'])
                logger.warn(f'[OPENAI] completion rate limit exceed, 第{retry_count+1}次重试')
                return self.reply_text(content, context, retry_count+1)
            else:
                return Reply(by=f'reply_text', type='TEXT', result='error', msg='提问太快啦，请休息一下再问我吧!')
        except Exception as e:
            # unknown exception
            logger.exception(e)
            session.reset_records()
            return Reply(by=f'reply_text', type='TEXT', result='error', msg='OpenAI出小差了, 请再问我一次吧!')

    def reply_img(self, content, context, retry_count=0):
        logger.debug(f'[OPENAI] reply_img content={content}')

        user_id = context['user_id']
        user_name = context['user_name']

        try:
            response = openai.Image.create(
                prompt=content,  # 图片描述
                n=1,             # 每次生成图片的数量
                size="512x512"   # 图片大小,可选有 256x256, 512x512, 1024x1024
            )
            image_url = response['data'][0]['url']
            logger.debug(f'[OPENAI] reply_img answer={image_url}')
            return Reply(by='openai_img', type='IMAGE', result='done', msg=image_url)
        except openai.error.RateLimitError as e:
            logger.warn(e)
            if retry_count < self.config['retry_times']:
                time.sleep(self.config['retry_interval'])
                logger.warn(f'[OPENAI] rate limit exceed, 第{retry_count+1}次重试')
                return self.reply_img(content, context, retry_count+1)
            else:
                return Reply(by='openai_img', type='TEXT', result='error', msg='提问太快啦，请休息一下再问我吧!')
        except Exception as e:
            logger.exception(e)
            return Reply(by='openai_img', type='TEXT', result='error', msg='图片生成失败, 请再问我一次吧!')
