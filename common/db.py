import os
from config import Config
from tinydb import TinyDB
from tinydb.table import Document
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware


class TinyDBHelper(object):
    @classmethod
    def db(cls, db_name) -> TinyDB:
        db_path = f'{Config.db_path()}/{db_name}'
        _dir = os.path.dirname(db_path)
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        return TinyDB(db_path, storage=CachingMiddleware(JSONStorage))


if __name__ == '__main__':
    import arrow
    from tinydb import Query, where
    with TinyDBHelper.db('test.json') as db:
        db.upsert(Document({'name': 'John', 'logged-in': True}, doc_id=12))
        # db.insert({'id': arrow.now().int_timestamp, 'value': arrow.now().format(), 'j': {'a': 0, 'b': True}})
        # db.insert({'id': arrow.now().int_timestamp, 'value': arrow.now().format(), 'j': {'a': 1, 'b': False}})
        print(db.all())
        # t = db.search(Query().j.a >= 1)
        # t.sort(key=lambda x: x['id'], reverse=True)
        # print(t)
