# -*- coding: utf-8 -*-
from scrapy.utils.serialize import ScrapyJSONEncoder

from .defaults import FILTER_CLS
from .utils import get_network, get_index_arr
from .queue import RedisQueue
import logging

logger = logging.getLogger(__name__)
default_serialize = ScrapyJSONEncoder().encode


class QueuePipeline(RedisQueue):
    """ 生成任务队列
    """

    local_ip = get_network('inet')
    logger = logger
    filter_cls = None

    def __init__(self, *args, **kwargs):
        self.filter_cls = get_index_arr(args, default={}).get("FILTER_CLS", FILTER_CLS)(*args, **kwargs)
        super(QueuePipeline, self).__init__(*args, **kwargs)

    def open_spider(self, spider):
        """ 启动爬虫的时候需要做的事情
        :param spider:
        :return:
        """
        pass

    @classmethod
    def from_crawler(cls, spider):
        """ 初始化爬虫所需的一些操作
        :param spider:
        :return:
        """
        return cls(spider.settings)

    def lose_spider(self, spider):
        """ 关闭爬虫的时候需要做的事情
        :param spider:
        :return:
        """
        pass

    def filter_cls_use_item(self, item, spider):
        """ 先来选择哪个过滤器处理 """
        result = 0

        filter_cls_name = None
        if self.filter_cls:
            filter_cls_name = self.filter_cls.__class__.__name__

        if "BloomFilter" in filter_cls_name:
            result = self.bloom_filter(item, spider)
        elif "RedisHashFilter" in filter_cls_name:
            result = self.redis_hash_filter(item, spider)
        return result

    def bloom_filter(self, item, spider):
        """ 使用布隆过滤器处理
        :param item:
        :param spider:
        :return:
        """
        return 0

    def redis_hash_filter(self, item, spider):
        """ 使用 redis hash 过滤器处理
        :param item:
        :param spider:
        :return:
        """
        return 0
