# -*- coding: utf-8 -*-
import hashlib

import math
import psutil
import six


def bytes_to_str(s, encoding='utf-8'):
    """Returns a str if a bytes object is given."""
    if six.PY3 and isinstance(s, bytes):
        return s.decode(encoding)
    return s


def gen_md5(str_con: str):
    """ 把输入的数据转换成MD5
    :param str_con: 输入的数据
    :type str_con: str
    :return:
    """
    hl = hashlib.md5()
    hl.update(str(str_con).encode(encoding='utf-8'))
    return hl.hexdigest()


def get_network(key=None):
    """ 这个程序是使用了第三方库
    :param key:
    :type key:
    :return:
    """
    __info = dict()
    info = psutil.net_if_addrs()
    for k, v in info.items():
        for item in v:
            if item[0] == 2 and not item[1] == '127.0.0.1':
                __info[k] = item[1]

    if key == "inet":
        for k, v in __info.items():
            return v
    return __info


def get_index_arr(arr: list, index=0, default=None):
    """ 这个函数的作用是根据 index 获取数组中的元素
    :param arr: 数组
    :param index: 数组中的索引位置
    :param default: 默认填充值
    :return:
    """
    if not isinstance(arr, (list, tuple)):
        return default

    if index >= len(arr):
        return default

    text = arr[index]
    if text in [None, '']:
        return default
    else:
        if isinstance(text, (bytes,)):
            return text.decode('utf-8').strip()
        return text


def slice_arr(arr: list, slice_len: int):
    """ 把数组按照给定的长度切割
    :param arr: 数组
    :type arr: list
    :param slice_len: 给定的长度
    :type slice_len: int
    :return:
    Example:
        Input:
            arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            slice_len = 3
        Output:
            [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11]]
    """
    return [
        arr[x * slice_len:(x + 1) * slice_len]
        for x in range(0, math.ceil(len(arr) / slice_len))
    ]
