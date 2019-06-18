# -*- coding: utf-8 -*-

"""
这个脚本主要的作用是实现 redis 版本的布隆过滤器
"""
import logging

import mmh3
import math

from scrapy_queue import connection, defaults

logger = logging.getLogger(__name__)


class BloomFilter(object):
    # 内置100个随机种子
    SEEDS = [
        543, 460, 171, 876, 796, 607, 650, 81, 837, 545, 591, 946, 846, 521, 913, 636, 878, 735, 414, 372,
        344, 324, 223, 180, 327, 891, 798, 933, 493, 293, 836, 10, 6, 544, 924, 849, 438, 41, 862, 648, 338,
        465, 562, 693, 979, 52, 763, 103, 387, 374, 349, 94, 384, 680, 574, 480, 307, 580, 71, 535, 300, 53,
        481, 519, 644, 219, 686, 236, 424, 326, 244, 212, 909, 202, 951, 56, 812, 901, 926, 250, 507, 739, 371,
        63, 584, 154, 7, 284, 617, 332, 472, 140, 605, 262, 355, 526, 647, 923, 199, 518
    ]
    logger = logger
    server = None

    def __init__(self, setting):
        """ 初始化布隆过滤器

        capacity: 是预先估计要去重的数量，初始1亿
        error_rate: 表示错误率
        """
        capacity = setting.get("CAPACITY", defaults.BLOOM_FILTER.get("capacity", 10000000))
        error_rate = 1 / float(capacity)

        if not self.server:
            self.server = connection.from_settings(setting)

        self.m = math.ceil(capacity * math.log2(math.e) * math.log2(1 / error_rate))  # 需要的总bit位数
        self.k = math.ceil(math.log1p(2) * self.m / capacity)  # 需要最少的hash次数
        self.mem = math.ceil(self.m / 8 / 1024 / 1024)  # 需要的多少M内存
        self.block_num = math.ceil(self.mem / 512)  # 需要多少个512M的内存块,value的第一个字符必须是ascii码，所有最多有256个内存块
        self.seeds = self.SEEDS[0:self.k]
        self.N = 2 ** 31 - 1

        self.name = 'BloomFilter'  # 定义一个默认的名字

    def __format_key(self, key):
        """ 格式化布隆过滤器的
        :param key:
        :return:
        """
        if not key:
            return self.name
        else:
            return key + ":" + self.name

    def filter_add(self, key, value):
        """ 这个函数的作用是把一个数加入到布隆过滤器中
        :param key: 输入的
        :param value:
        :return: 插入成功是0，插入失败返回 1
        """
        __key = self.__format_key(key)
        murmur_hash = self.get_murmur_hash(value)
        return self._redis_batch_exec('setbit', __key, murmur_hash, 1)

    def filter_is_exist(self, key, value):
        """ 判断是否是在布隆过滤器的实现
        :param key: 输入的key
        :param value: 输入的值
        :return:
        """
        __key = self.__format_key(key)
        murmur_hash = self.get_murmur_hash(value)
        return self._redis_batch_exec('getbit', __key, murmur_hash)

    def get_murmur_hash(self, value):
        """ Murmur 哈希
        百度百科： https://baike.baidu.com/item/Murmur哈希/22689658?fr=aladdin
        :param value: 输入的值
        :return: 返回一个 Murmur哈希
        """
        murmur_hash = list()
        for seed in self.seeds:
            __hash = mmh3.hash(value, seed)
            if __hash >= 0:
                murmur_hash.append(__hash % self.m)
            else:
                murmur_hash.append((self.N - __hash) % self.m)
        return murmur_hash

    def _redis_batch_exec(self, exec_type, key, value, *args, **kwargs):
        """ 这个函数的作用是布隆过滤器用来批量执行数据 """
        command_arr = []
        if args:
            values = ",".join(map(lambda x: "'{}'".format(x), args))
        else:
            values = ''

        if values:
            values = "," + values

        if kwargs:
            kv = ''
            for k, v in kwargs.items():
                kv = kv + ",{}={}".format(str(k), str(v))
            values = values + kv

        for line in value:
            command_arr.append("pipe.{}('{}',{}{})".format(exec_type, key, line, values))

        init_status = True
        results = self.server.batch_exec(key=key, command_arr=command_arr)
        if results and isinstance(results, (list, tuple)):
            for line in results:
                init_status = init_status & bool(line)
            return init_status
        return False
