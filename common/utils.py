import os
import math
import base64
import time
import threading
from typing import List, Dict, Callable, Optional
from datetime import datetime, timedelta
from pytz import timezone
from collections import defaultdict
from functools import wraps


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
