import arrow
from config import Config
from common.db import tinydb
from tinydb import Query
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage
from .token import Token
from .profile import Profile


class Session(object):
    @classmethod
    def _db(cls):
        return tinydb('openai/session.json', storage=CachingMiddleware(JSONStorage))

    def __init__(self, user_id):
        self.user_id = user_id
        self.table_name = user_id
        self.profile = Profile(self.user_id)
        self.character = self.profile.get('character', Config.openai('character'))
        self.max_query_tokens = Config.openai('max_query_tokens')

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

    def get_records(self, max_tokens):
        with self._db() as db:
            qry = Query()
            tab = db.table(self.table_name)
            _reset_r = tab.search(qry.action == 'reset')
            _reset_r.sort(key=lambda x: x['created_at'], reverse=False)
            if len(_reset_r) > 0:
                _last_reset_at = _reset_r[-1]['created_at']
                _records = tab.search((qry.action == 'add') & (qry.created_at > _last_reset_at))
            else:
                _records = tab.all()
            _records.sort(key=lambda x: x['created_at'], reverse=False)
        self._discard_exceed_records(_records, max_tokens)
        return _records

    def reset_records(self):
        with self._db() as db:
            tab = db.table(self.table_name)
            tab.insert({
                'action': 'reset',
                'question': '',
                'answer': '',
                'created_at': arrow.now().int_timestamp,
            })

    def clear_records(self):
        with self._db() as db:
            db.drop_table(self.table_name)

    def add_record(self, question, answer):
        with self._db() as db:
            tab = db.table(self.table_name)
            tab.insert({
                'action': 'add',
                'question': question,
                'answer': answer,
                'created_at': arrow.now().int_timestamp,
            })

    def build_query(self, content):
        prompt = self.character
        prompt += '\n#\n'
        records = self.get_records(self.max_query_tokens)
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
    session = Session('bz')
    # session.reset_records()
    # session.add_record('XXX1', 'YYYY2')
    print(session.build_query('zzzzz1'))
