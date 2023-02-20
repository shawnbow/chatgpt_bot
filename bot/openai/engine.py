# encoding:utf-8
import re
import openai
import time
from bot.bot import Bot
from config import Config
from common.log import logger
from common.data import Reply
from .session import SessionManager


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
        sm = SessionManager(user_id)
        joined_session = sm.joined_session

        if content.startswith('help'):
            msg = \
                '命令格式如下: \n' \
                '/help\n' \
                '/新建对话%[标题]%[性格]\n' \
                '/对话列表\n' \
                '/切换对话%<对话ID>\n' \
                '/重启对话\n' \
                '/最近对话\n' \
                '/性格\n' \
                '/性格%你是666, 一个由OpenAI训练的大型语言模型, 你旨在回答并解决人们的任何问题，并且可以使用多种语言与人交流。\n'
            return Reply(by='openai_cmd', type='TEXT', result='done', msg=msg)

        elif content.startswith('新建对话'):
            _tmp = content.split('%', 2)
            if len(_tmp) == 2:
                new_session_id = sm.new_session(title=_tmp[1])
            elif len(_tmp) == 3:
                new_session_id = sm.new_session(title=_tmp[1], character=_tmp[2])
            else:
                new_session_id = sm.new_session()
            new_session = sm.join_session(new_session_id)
            return Reply(by='openai_cmd', type='TEXT', result='done', msg=f'新建对话: {new_session["title"]}, 性格: {new_session["character"]}')

        elif content.startswith('对话列表'):
            sessions = sm.sessions
            msg = ''
            for s in sessions:
                if s['session_id'] == joined_session['session_id']:
                    msg += f'\n>>>>'
                else:
                    msg += f'\n----'
                msg += f'对话ID: {s["session_id"]}, 标题: {s["title"]}, 性格: {s["character"]}'
            return Reply(by='openai_cmd', type='TEXT', result='done', msg=msg)

        elif content.startswith('切换对话%'):
            _tmp = content.split('%', 1)
            if len(_tmp) == 2:
                sessions = sm.sessions
                session_id = _tmp[1].strip()
                for s in sessions:
                    if s['session_id'] == session_id:
                        session = sm.join_session(session_id)
                        return Reply(by='openai_cmd', type='TEXT', result='done', msg=f'切换对话: {session["title"]}, 性格: {session["character"]}')
            return Reply(by='openai_cmd', type='TEXT', result='error', msg=f'对话不存在!')

        elif content.startswith('重启对话'):
            sm.reset_records(joined_session['session_id'])
            return Reply(by='openai_cmd', type='TEXT', result='done', msg='对话已重启!')

        elif content.startswith('最近对话'):
            return Reply(
                by='openai_cmd', type='TEXT', result='done',
                msg=sm.build_query(joined_session['session_id'], ''))

        elif content.startswith('性格'):
            _tmp = content.split('%', 1)
            if len(_tmp) == 2:
                sm.set_session(joined_session['session_id'], character=_tmp[1])
                msg = f'对话{joined_session["title"]}的性格设置为: {_tmp[1]}'
                return Reply(by='openai_cmd', type='TEXT', result='done', msg=msg)
            else:
                msg = joined_session.get('character', Config.openai('character'))
                return Reply(by='openai_cmd', type='TEXT', result='done', msg=f'对话{joined_session["title"]}的性格是: {msg}')

        else:
            return Reply(by='openai_cmd', type='TEXT', result='error', msg='不支持该命令!')

    def reply_code(self, content, context, retry_count=0):
        logger.debug(f'[OPENAI] reply_code content={content}')

        user_id = context['user_id']
        user_name = context['user_name']

        try:
            model = self.config['code_model']
            max_tokens = self.config['max_reply_tokens']
            query = content
            logger.debug(f'[OPENAI] create completion model={model} prompt={query}')
            response = openai.Completion.create(
                model=model,  # 对话模型的名称
                prompt=query,
                temperature=0.9,  # 值在[0,1]之间，越大表示回复越具有不确定性
                max_tokens=max_tokens,  # 回复最大的字符数
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
        sm = SessionManager(user_id)
        joined_session = sm.joined_session
        session_id = joined_session['session_id']

        try:
            model = self.config['text_model']
            max_tokens = self.config['max_reply_tokens']
            query = sm.build_query(session_id, content)
            logger.debug(f'[OPENAI] create completion model={model} prompt={query}')
            response = openai.Completion.create(
                model=model,  # 对话模型的名称
                prompt=query,
                temperature=0.9,  # 值在[0,1]之间，越大表示回复越具有不确定性
                max_tokens=max_tokens,  # 回复最大的字符数
                top_p=1,
                frequency_penalty=0.0,  # [-2,2]之间，该值越大则更倾向于产生不同的内容
                presence_penalty=0.0,  # [-2,2]之间，该值越大则更倾向于产生不同的内容
                stop=["\n#\n"]
            )
            answer = response.choices[0]['text'].strip()  # replace('<|endoftext|>', '')
            logger.debug(f'[OPENAI] reply_text answer={answer}')
            sm.add_record(session_id, content, answer)
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
            # sm.reset_records(session_id)
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
