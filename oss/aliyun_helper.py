from config import Config
import arrow
import oss2
from common.utils import Fetcher
from common.db import TinyDBHelper
from tinydb import Query
from tinydb.table import Document
import hashlib
import json
import time
from common.log import logger

oss_config = Config.get('oss')['aliyun']


class Helper:
    auth = oss2.Auth(oss_config['access_key'], oss_config['secret_key'])

    @classmethod
    def upload_url(cls, url, bucket=oss_config['bucket'], retry_count=0):
        data, file_type, file_ext = Fetcher.fetch_file_data(url)
        if not data:
            logger.debug(f'[ALY] failed to download {url}')
            return None
        else:
            logger.debug(f'[ALY] file {file_type}/{file_ext} {url} fetch to mem')

        _now = arrow.now().float_timestamp
        _date = arrow.now().format('YYYY_MM_DD')
        _hash = hashlib.md5((url + str(_now)).encode(encoding="UTF-8")).hexdigest()
        filename = f'{_date}/{file_type}/{_hash}{file_ext}'

        _bucket = oss2.Bucket(cls.auth, oss_config['endpoint'], bucket)
        ret = _bucket.put_object(filename, data=data)
        logger.debug(f'[ALY] put_object return ret.request_id={ret.request_id}, ret.status={ret.status}, ret.etag={ret.etag}')

        # 判断是否上传成功
        if ret.status != 200:
            if retry_count < 2:
                time.sleep(1)
                return cls.upload_url(url, retry_count+1)
            else:
                return None

        return oss_config['bucket_url'] + filename
