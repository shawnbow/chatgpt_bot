import os
import math
import re
import base64
import time
import threading
from typing import List, Dict, Callable, Optional
from datetime import datetime, timedelta
from pytz import timezone
from collections import defaultdict
from functools import wraps


class MarkdownUtils:

    @classmethod
    def extract_images(cls, text: str):
        # Check for headings
        pattern = r"!\[.*\]\((.*?)\)"
        return re.findall(pattern, text)


# 数字编码器
class IntEncoder:
    @classmethod
    def int_to_bytes(cls, x: int) -> bytes:
        return x.to_bytes((x.bit_length() + 7) // 8, 'big')

    @classmethod
    def int_from_bytes(cls, x_bytes: bytes) -> int:
        return int.from_bytes(x_bytes, 'big')

    @classmethod
    def encode_int(cls, i: int, prefix='int'):
        return prefix + base64.b64encode(cls.int_to_bytes(i)).decode('ascii').replace('=', '').replace('/', '').replace('+', '')

    @classmethod
    def encode_now(cls, prefix='time'):
        # 946684800000 -> 2000-01-01 00:00:00 UTC
        return cls.encode_int(int(time.time() * 1000), prefix=prefix)


# defaultdict 增强版
class BoostDict(defaultdict):
    def __init__(self, boost_factory):
        super().__init__(None)
        self.boost_factory = boost_factory

    def __missing__(self, key):
        if self.boost_factory is None:
            raise KeyError(key)
        self[key] = ret = self.boost_factory(key)
        return ret
