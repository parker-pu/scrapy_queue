# -*- coding: utf-8 -*-

"""
这个脚本主要的作用是实现 redis 版本的set过滤器，其实就是使用redis的特性
"""
import logging

from scrapy_queue import connection
from scrapy_queue.utils import (
    get_index_arr,
    bytes_to_str,
    gen_md5
)

logger = logging.getLogger(__name__)


class RedisHashFilter(object):
    logger = logger
    server = None

    def __init__(self, setting):
        """ 初始化　Redis 所需的一些参数
        """

        if not self.server:
            self.server = connection.from_settings(setting)

        self.name = 'RedisSetFilter'  # 定义一个默认的名字

    def __format_key(self, key):
        """ 格式化布隆过滤器的
        :param key:
        :return:
        """
        if not key:
            return self.name
        else:
            return key + ":" + self.name

    @staticmethod
    def __init_hash_table(*args):
        """ 这个函数的作用是初始化需要存入的 hash table 的数据
        :param args:
        :return:
        """
        result = {}
        for k in args:
            _k = gen_md5(k)
            result[_k] = 1
        return result

    def filter_add(self, key, *args):
        """ 判断是否存在是正对redis　set的操作
        :param key: 输入的key
        :param args: 需要存入的数据
        """
        if len(args) > 255:
            raise Exception("args greater 255")

        __key = self.__format_key(key)
        result = self.server.exec('hmset', __key, format_dict=self.__init_hash_table(*args))
        return get_index_arr(result)

    def filter_is_exist(self, key, *args):
        """ 判断是否存在是正对redis　set的操作
        :param key: 输入的key
        :param args: 输入的值
        :return:
        """
        if len(args) > 255:
            raise Exception("args greater 255")

        __key = self.__format_key(key)
        result = self.server.exec('hmget', __key, *[gen_md5(x) for x in args])
        return [True if bytes_to_str(x) else False for x in get_index_arr(result, default=[])]
