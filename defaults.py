# -*- coding: utf-8 -*-
# For standalone use.
from .filter.redis_hash import RedisHashFilter
from .redis import RedisServer

FILTER_CLS = RedisHashFilter
REDIS_CLS = RedisServer
REDIS_ENCODING = 'utf-8'
# Sane connection defaults.
REDIS_PARAMS = {
    'socket_timeout': 30,
    'socket_connect_timeout': 30,
    'retry_on_timeout': True,
    'encoding': REDIS_ENCODING,
}

BLOOM_FILTER = {
    "capacity": 100000000,
    "error_rate": 0.00000001
}
