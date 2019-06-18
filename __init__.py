# -*- coding: utf-8 -*-
"""
这个一个包的说明文件,这个包是仿照 scrapy-redis 这个包来写的

这个模块所需的全部依赖应该都只是在本模块里面包含
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .spiders import RedisQueueSpider
from .spiders import RedisQueueCrawlSpider
from .pipelines import QueuePipeline
from .filter.bloom import BloomFilter
from .filter.redis_hash import RedisHashFilter

__all__ = [
    'RedisQueueSpider',
    'RedisQueueCrawlSpider',
    'QueuePipeline',
    'BloomFilter',
    'RedisHashFilter'
]

__version__ = '1.0.0'
