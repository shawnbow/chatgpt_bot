from common.db import tinydb
from tinydb import Query
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage


class Profile:
    @classmethod
    def _db(cls):
        return tinydb('openai/profile.json', storage=CachingMiddleware(JSONStorage))

    def __init__(self, user_id):
        self.user_id = user_id

    def set(self, key, value):
        with self._db() as db:
            qry = Query()
            tab = db.table('profile')
            tab.upsert({
                'uid': self.user_id,
                key: value,
            }, (qry.uid == self.user_id))

    def get(self, key, default=None):
        with self._db() as db:
            qry = Query()
            tab = db.table('profile')
            _tmp = tab.search(qry.uid == self.user_id)
            if _tmp:
                return _tmp[0].get(key, default)
            else:
                return default


if __name__ == '__main__':
    p = Profile('bz')
    p.set('character', '你是666')
    print(p.get('character'))
