# coding=utf-8
"""
这个类的作用是操作 redis
"""
import logging

from scrapy_queue.redis import WatchError

logger = logging.getLogger(__name__)


class RedisServer(object):
    """
    这个类的作用是用来操作 redis 数据库
    """
    logger = logger

    def __init__(self, *args, **kwargs):
        """ 初始化类
        :param redis_kwargs:
        """
        self.kwargs = kwargs
        self.conn = redis.StrictRedis(
            connection_pool=redis.ConnectionPool(**self.kwargs)
        )

    def exec(self, add_type='set', key=None, *args, **kwargs):
        """ 这个函数的作用是用来操作数据库
        :param key: key
        :param add_type: 操作的类型
        :return:
        """
        # 数据存入redis，使用管道的方式
        with self.conn.pipeline() as pipe:
            while True:
                try:
                    # 监听一个 key
                    pipe.watch(key)

                    # 事物开始
                    pipe.multi()

                    if args:
                        values = ",".join(map(lambda x: "'{}'".format(x), args))
                    else:
                        values = ''

                    if values:
                        values = "," + values

                    exec_cmd = None
                    if kwargs:
                        if "format_dict" in kwargs.keys():
                            values = kwargs.get("format_dict", {})
                            exec_cmd = "pipe.{}('{}',{})".format(add_type, key, values)
                        else:
                            kv = ''
                            for k, v in kwargs.items():
                                kv = kv + ",{}={}".format(str(k), str(v))
                            values = values + kv

                    if not exec_cmd:
                        exec_cmd = "pipe.{}('{}'{})".format(add_type, key, values)

                    eval(exec_cmd)
                    result = pipe.execute()
                    return result
                except WatchError as _:
                    continue
                except Exception as e:
                    self.logger.warning("<{}>, <{}>, <{}>, <{}> error <{}>".format(
                        add_type, key, args, kwargs, e.args))
                    return None
                finally:
                    # 重试直到 key 不被其它客户端影响
                    pipe.reset()

    def batch_exec(self, key, command_arr, *args, **kwargs):
        """ 这个函数的作用是用来操作数据库

        command_arr 格式如下：
            [pipe.set("name","张三"),pipe.set("name","张三") ...]
        :return:
        """
        if not isinstance(command_arr, (tuple, list)):
            raise Exception("命令格式错误，应该是数组类型")

        # 数据存入redis，使用管道的方式
        with self.conn.pipeline() as pipe:
            while True:
                try:
                    # 监听一个 key
                    pipe.watch(key)

                    # 事物开始
                    pipe.multi()
                    for line_command in command_arr:
                        eval("{}".format(line_command))
                    result = pipe.execute()
                    return result
                except WatchError as _:
                    continue
                except Exception as e:
                    self.logger.warning("<{}>, <{}>, <{}> error <{}>".format(
                        key, args, kwargs, e.args))
                    continue
                finally:
                    # 重试直到 key 不被其它客户端影响
                    pipe.reset()
