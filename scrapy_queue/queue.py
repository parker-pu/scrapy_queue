# -*- coding: utf-8 -*-
"""
这个脚本的作用是用来实现 Redis 的队列
"""
import logging

from scrapy_queue import connection
from scrapy_queue.utils import get_index_arr

logger = logging.getLogger(__name__)


class RedisQueue(object):
    """ 这个类的作用是用来实现 Redis 的队列的功能

    队列左进右出
    """
    logger = logger
    server = None

    def __init__(self, setting):
        """ 初始化队列的设置
        """
        if not self.server:
            self.server = connection.from_settings(setting)

    def qsize(self, key):
        """ 返回队列里面list内元素的数量
        """
        return self.server.exec('llen', key)

    def put(self, key, *args):
        """ 从队列的左边加入元素
        """
        return self.server.exec('lpush', key, *args)  # 添加新元素到队列最左边

    def pop(self, key, *args, **kwargs):
        """ 从队列右边 pop 出元素
        :param key: 队列名
        :return:
        """
        try:
            result = self.server.exec('brpop', key, *args, **kwargs)
            item = get_index_arr(get_index_arr(result, default=[]))
        except Exception as e:
            self.logger.warning("<brpop> pop {}".format(key, e.args))
            item = None
        return item

    def move_pop(self, key1, key2, *args, **kwargs):
        """ 从 key1 的右边 pop 出一个元素放入到 key2 的左边
        :param key1:
        :param key2:
        :return:
        """
        try:
            result = self.server.exec('brpoplpush', key1, key2, timeout=0, *args, **kwargs)
            item = get_index_arr(result)
        except Exception as e:
            self.logger.warning("<brpoplpush> move pop {} to {} {}".format(key1, key2, e.args))
            item = None
        return item

    def move_all(self, key1, key2, *args, **kwargs):
        """ 把key1的所有元素移动到key2里面

        元素的移动使用 brpoplpush，因为，考虑到事务性
        :param key1:
        :param key2:
        :return:
        """
        try:
            while bool(get_index_arr(self.server.exec('exists', key1), default=False)):
                self.move_pop(key1, key2, *args, **kwargs)
        except Exception as e:
            self.logger.warning("<move_all> move_all {} to {} {}".format(key1, key2, e.args))
        return True
