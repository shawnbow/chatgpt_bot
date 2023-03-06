from config import Config
import arrow
from qingstor.sdk.service.qingstor import QingStor
from qingstor.sdk.config import Config as QingStorConfig
from common.utils import Fetcher
from common.db import TinyDBHelper
from tinydb import Query
from tinydb.table import Document
import hashlib
import json
import time
from common.log import logger

oss_config = Config.get('oss')['qing']


class Helper:
    qingstor = QingStor(QingStorConfig(oss_config['access_key'], oss_config['secret_key']))

    @classmethod
    def upload_url(cls, url, bucket=oss_config['bucket'], retry_count=0):
        data, file_type, file_ext = Fetcher.fetch_file_data(url)
        if not data:
            logger.debug(f'[QING] failed to download {url}')
            return None
        else:
            logger.debug(f'[QING] file {file_type}/{file_ext} {url} fetch to mem')

        _now = arrow.now().float_timestamp
        _date = arrow.now().format('YYYY_MM_DD')
        _hash = hashlib.md5((url + str(_now)).encode(encoding="UTF-8")).hexdigest()
        filename = f'{_date}/{file_type}/{_hash}{file_ext}'
        _bucket = cls.qingstor.Bucket(bucket, oss_config['endpoint'])
        ret = _bucket.put_object(filename, body=data)
        logger.debug(f'[QING] put_object return {ret.content}, ret.status={ret.status_code}')

        # 判断是否上传成功
        if ret.status_code != 201:
            if retry_count < 2:
                time.sleep(1)
                return cls.upload_url(url, retry_count+1)
            else:
                return None

        return oss_config['bucket_url'] + filename
