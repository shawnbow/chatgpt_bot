from config import Config
import arrow
import qiniu
from common.utils import Fetcher
from common.db import TinyDBHelper
from tinydb import Query
from tinydb.table import Document
import hashlib
import json
import time
from common.log import logger

oss_config = Config.get('oss')['qiniu']


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
        expires = oss_config['token_expires']

        _cache = cls.token_cache(bucket)
        if _cache and _now - _cache['created_at'] <= expires:
            token = _cache['token']
        else:
            access_key = oss_config['access_key']
            secret_key = oss_config['secret_key']
            q = qiniu.Auth(access_key, secret_key)
            # 生成上传 Token，可以指定过期时间等
            token = q.upload_token(bucket, expires=expires)
            cls.token_cache(bucket, {
                'token': token,
                'created_at': _now,
            })
        return token

    @classmethod
    def upload_url(cls, url, bucket=oss_config['bucket'], retry_count=0):
        data, file_type, file_ext = Fetcher.fetch_file_data(url)
        if not data:
            logger.debug(f'[QN] failed to download {url}')
            return None
        else:
            logger.debug(f'[QN] {file_type}/{file_ext} {url} fetch to mem')

        _now = arrow.now().float_timestamp
        _date = arrow.now().format('YYYY_MM_DD')
        _hash = hashlib.md5((url + str(_now)).encode(encoding="UTF-8")).hexdigest()
        filename = f'{_date}/{file_type}/{_hash}{file_ext}'

        token = cls.get_token(bucket)
        ret1, ret2 = qiniu.put_data(token, filename, data=data)
        logger.debug(f'[QN] put_data return ret1={str(ret1)}， ret2={str(ret2)}')

        # 判断是否上传成功
        if ret2.status_code != 200:
            if retry_count < 2:
                time.sleep(1)
                return cls.upload_url(url, retry_count+1)
            else:
                return None

        return oss_config['bucket_url'] + ret1.get('key')
