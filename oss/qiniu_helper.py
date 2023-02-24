from config import Config
import arrow
import qiniu
from common.utils import Downloader
from common.db import TinyDBHelper
from tinydb import Query
from tinydb.table import Document
import hashlib
import json
import time
from common.log import logger

qiniu_config = Config.get('qiniu')


class Helper:
    @classmethod
    def token_cache(cls, bucket, update_cache=None):
        with TinyDBHelper.db('qiniu/token.json') as db:
            _t = db.table(bucket)
            if update_cache:
                _t.upsert(Document(update_cache, doc_id=0))
            _tmp = _t.get(doc_id=0)
            return _tmp if _tmp else {'token': '', 'created_at': 0}

    @classmethod
    def get_token(cls, bucket):
        _now = arrow.now().int_timestamp
        expires = qiniu_config['token_expires']

        _cache = cls.token_cache(bucket)
        if _cache and _now - _cache['created_at'] <= expires:
            token = _cache['token']
        else:
            access_key = qiniu_config['access_key']
            secret_key = qiniu_config['secret_key']
            q = qiniu.Auth(access_key, secret_key)
            # 生成上传 Token，可以指定过期时间等
            token = q.upload_token(bucket, expires=expires)
            cls.token_cache(bucket, {
                'token': token,
                'created_at': _now,
            })
        return token

    @classmethod
    def upload_url(cls, url, bucket=qiniu_config['bucket'], retry_count=0):
        _now = arrow.now().float_timestamp
        token = cls.get_token(bucket)
        data, file_type, file_suffix = Downloader.fetch_file_bytes(url)
        if not data:
            logger.debug(f'[QN] failed to download {url}')
            return None
        else:
            logger.debug(f'[QN] file {file_type}/{file_suffix} {url} fetch to mem')

        filename = f'{file_type}/{hashlib.md5((url + str(_now)).encode(encoding="UTF-8")).hexdigest()}.{file_suffix}'
        ret1, ret2 = qiniu.put_data(token, filename, data=data)
        logger.debug(f'[QN] put_data return ret1={str(ret1)}， ret2={str(ret2)}')

        # 判断是否上传成功
        if ret2.status_code != 200:
            if retry_count < 2:
                time.sleep(1)
                return cls.upload_url(url, retry_count+1)
            else:
                return None

        return qiniu_config['url'] + ret1.get('key')
