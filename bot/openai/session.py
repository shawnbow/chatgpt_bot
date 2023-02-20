import arrow
from config import Config
from common.utils import IntEncoder
from common.db import TinyDBHelper
from tinydb.table import Document
from tinydb import Query
from .token import Token
import hashlib


class SessionManager:
    def __init__(self, user_id, platform='DingTalk'):
        self.user_id = user_id
        self.session_db = f'openai/{hashlib.md5(user_id.encode(encoding="UTF-8")).hexdigest()}.json'
        self.t_user_profile = 'user_profile'
        self.t_sessions_profile = 'sessions_profile'
        if not self.user_profile:
            self.set_user_profile(user_id=user_id, joined_session='', platform=platform, state=1)

    @property
    def user_profile(self):
        with TinyDBHelper.db(self.session_db) as db:
            _t = db.table(self.t_user_profile)
            _tmp = _t.get(doc_id=0)
            return _tmp if _tmp else dict()

    def set_user_profile(self, **kwargs):
        with TinyDBHelper.db(self.session_db) as db:
            _t = db.table(self.t_user_profile)
            _t.upsert(Document(kwargs, doc_id=0))

    @property
    def sessions(self):
        with TinyDBHelper.db(self.session_db) as db:
            _t = db.table(self.t_sessions_profile)
            _tmp = _t.all()
            return _tmp

    def get_session(self, session_id):
        with TinyDBHelper.db(self.session_db) as db:
            qry = Query()
            _t = db.table(self.t_sessions_profile)
            _tmp = _t.search(qry.session_id == session_id)
            return _tmp[0] if _tmp else dict()

    def set_session(self, session_id, **kwargs):
        with TinyDBHelper.db(self.session_db) as db:
            qry = Query()
            _t = db.table(self.t_sessions_profile)
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

        session_id = IntEncoder.encode_now()
        self.set_session(session_id, title=title, character=character)
        return session_id

    def join_session(self, session_id):
        self.set_user_profile(joined_session=session_id)
        return self.get_session(session_id)

    @property
    def joined_session(self):
        session_id = self.user_profile.get('joined_session', '')
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
                'action': 'reset',
                'question': '',
                'answer': '',
                'created_at': int(arrow.now().float_timestamp * 1000),
            })

    def clear_records(self, session_id):
        with TinyDBHelper.db(self.session_db) as db:
            db.drop_table(session_id)

    def add_record(self, session_id, question, answer):
        with TinyDBHelper.db(self.session_db) as db:
            _t = db.table(session_id)
            _t.insert({
                'action': 'add',
                'question': question,
                'answer': answer,
                'created_at': int(arrow.now().float_timestamp * 1000),
            })

    def build_query(self, session_id, content):
        prompt = self.get_session(session_id).get('character', Config.openai('character'))
        prompt += '\n#\n'
        records = self.get_records(session_id, Config.openai('max_query_tokens'))
        if records:
            for _r in records:
                prompt += 'Q: ' + _r["question"] + '\n' + \
                          'A: ' + _r["answer"] + \
                          '\n#\n'
            prompt += "Q: " + content + '\n' + \
                      'A: '
            return prompt
        else:
            return prompt + "Q: " + content + "\nA: "


if __name__ == '__main__':
    sm = SessionManager('bz')
    # sm.new_session('音乐家', '你是666')
    print(sm.get_session('qgShI6s'))
    sm.add_record('qgShI6s', 'QQQ', 'AAA')
    print(sm.build_query('qgShI6s', 'test'))
    sm.join_session('qgShI6s')
    print(sm.user_profile)
