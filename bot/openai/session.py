import arrow
from config import Config
from common.data import Context
from common.utils import IntEncoder
from common.db import TinyDBHelper
from tinydb.table import Document
from tinydb import Query
from .token import Token
import hashlib


# SessionSet -> Sessions -> Records
# 会话组      -> 会话      -> 对话记录
class SessionManager:
    def __init__(self, context: Context):
        self.context = context
        self.user_id = context.user_id
        self.user_name = context.user_name
        self.group_id = context.group_id
        self.is_group_chat = context.is_group_chat
        self.ss_id = self.group_id if self.is_group_chat else self.user_id

        self.session_db = f'openai/sessions/' \
                          f'{"group" if self.is_group_chat else "user"}/' \
                          f'{hashlib.md5(self.ss_id.encode(encoding="UTF-8")).hexdigest()}.json'
        self.t_session_set = 'session_set'
        self.t_sessions = 'sessions'

        if not self.session_set:
            # init user profile for new user
            self.set_session_set(
                ss_id=self.ss_id,
                is_group_chat=self.is_group_chat,
                joined_session='',
                platform=self.context.platform,
                created_at=int(arrow.now().float_timestamp * 1000),
                state=1)

    @property
    def session_set(self):
        with TinyDBHelper.db(self.session_db) as db:
            _t = db.table(self.t_session_set)
            _tmp = _t.get(doc_id=0)
            return _tmp if _tmp else dict()

    def set_session_set(self, **kwargs):
        with TinyDBHelper.db(self.session_db) as db:
            _t = db.table(self.t_session_set)
            _t.upsert(Document(kwargs, doc_id=0))

    @property
    def sessions(self):
        with TinyDBHelper.db(self.session_db) as db:
            _t = db.table(self.t_sessions)
            _tmp = _t.all()
            return _tmp

    def get_session(self, session_id):
        with TinyDBHelper.db(self.session_db) as db:
            qry = Query()
            _t = db.table(self.t_sessions)
            _tmp = _t.search(qry.session_id == session_id)
            return _tmp[0] if _tmp else dict()

    def set_session(self, session_id, **kwargs):
        with TinyDBHelper.db(self.session_db) as db:
            qry = Query()
            _t = db.table(self.t_sessions)
            kwargs.update({
                'session_id': session_id,
            })
            _t.upsert(kwargs, qry.session_id == session_id)

    def new_session(self, title='', character=''):
        _now = arrow.now().format("YYMMDD_HHmmss")
        if title:
            title = f'{_now}:{title}'
        else:
            title = _now

        if not character:
            character = Config.openai('character')

        session_id = IntEncoder.encode_now(prefix='session')
        self.set_session(session_id, title=title, character=character, created_at=int(arrow.now().float_timestamp * 1000))
        return session_id

    def join_session(self, session_id):
        self.set_session_set(joined_session=session_id)
        return self.get_session(session_id)

    def remove_session(self, session_id):
        with TinyDBHelper.db(self.session_db) as db:
            qry = Query()
            db.drop_table(session_id)
            _t = db.table(self.t_sessions)
            _t.remove(qry.session_id == session_id)

    @property
    def joined_session(self):
        session_id = self.session_set.get('joined_session', '')
        if not session_id:
            session_id = self.new_session()
            return self.join_session(session_id)
        return self.get_session(session_id)

    def get_records(self, session_id, max_tokens):
        with TinyDBHelper.db(self.session_db) as db:
            qry = Query()
            _t = db.table(session_id)
            _reset_r = _t.search(qry.action == 'reset')
            _reset_r.sort(key=lambda x: x['created_at'], reverse=False)
            if len(_reset_r) > 0:
                _last_reset_at = _reset_r[-1]['created_at']
                _records = _t.search((qry.action == 'add') & (qry.created_at > _last_reset_at))
            else:
                _records = _t.all()
            _records.sort(key=lambda x: x['created_at'], reverse=False)
        self._discard_exceed_records(_records, max_tokens)
        return _records

    def get_all_records(self, session_id):
        with TinyDBHelper.db(self.session_db) as db:
            _t = db.table(session_id)
            _tmp = _t.all()
            _tmp.sort(key=lambda x: x['created_at'], reverse=False)
            return _tmp

    @classmethod
    def _discard_exceed_records(cls, records, max_tokens):
        count = 0
        count_list = list()
        for i in range(len(records)-1, -1, -1):
            # count tokens of conversation list
            _r = records[i]
            count += len(Token.get(_r["question"])) + len(Token.get(_r["answer"]))
            count_list.append(count)

        for c in count_list:
            if c > max_tokens:
                # pop first record
                records.pop(0)

    def reset_records(self, session_id):
        with TinyDBHelper.db(self.session_db) as db:
            _t = db.table(session_id)
            _t.insert({
                'id': IntEncoder.encode_now(prefix='id'),
                'action': 'reset',
                'question': '',
                'answer': '',
                'user_id': self.user_id,
                'user_name': self.user_name,
                'created_at': int(arrow.now().float_timestamp * 1000),
            })

    def clear_records(self, session_id):
        with TinyDBHelper.db(self.session_db) as db:
            db.drop_table(session_id)

    def add_record(self, session_id, question, answer):
        with TinyDBHelper.db(self.session_db) as db:
            _t = db.table(session_id)
            _t.insert({
                'id': IntEncoder.encode_now(prefix='id'),
                'action': 'add',
                'question': question,
                'answer': answer,
                'user_id': self.user_id,
                'user_name': self.user_name,
                'created_at': int(arrow.now().float_timestamp * 1000),
            })

    def build_prompt(self, session_id, query):
        prompt = self.get_session(session_id).get('character', Config.openai('character'))
        prompt += '\n#\n'
        records = self.get_records(session_id, Config.openai('max_query_tokens'))
        if records:
            for _r in records:
                prompt += 'Q: ' + _r["question"] + '\n' + \
                          'A: ' + _r["answer"] + \
                          '\n#\n'
            prompt += "Q: " + query + '\n' + \
                      'A: '
            return prompt
        else:
            return prompt + "Q: " + query + "\nA: "


if __name__ == '__main__':
    pass
