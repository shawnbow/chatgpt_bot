import os
from config import Config
from tinydb import TinyDB


# tinydb factory
def tinydb(db_name: str, *args, **kwargs) -> TinyDB:
    db_path = f'{Config.db_path()}/{db_name}'
    _dir = os.path.dirname(db_path)
    if not os.path.exists(_dir):
        os.makedirs(_dir)
    return TinyDB(db_path, *args, **kwargs)


if __name__ == '__main__':
    import arrow
    from tinydb import Query, where
    from tinydb.middlewares import CachingMiddleware
    from tinydb.storages import JSONStorage
    with tinydb('test.json', storage=CachingMiddleware(JSONStorage)) as db:
        db.insert({'id': arrow.now().int_timestamp, 'value': arrow.now().format(), 'j': {'a': 0, 'b': True}})
        db.insert({'id': arrow.now().int_timestamp, 'value': arrow.now().format(), 'j': {'a': 1, 'b': False}})
        print(db.all())
        t = db.search(Query().j.a >= 1)
        t.sort(key=lambda x: x['id'], reverse=True)
        print(t)
