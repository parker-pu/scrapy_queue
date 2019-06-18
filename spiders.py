# -*- coding: utf-8 -*-

from scrapy import signals
from scrapy.exceptions import DontCloseSpider
from scrapy.spiders import Spider, CrawlSpider

from .queue import RedisQueue
from . import defaults
from .utils import bytes_to_str, get_network
import logging

logger = logging.getLogger(__name__)


class QueueMixin(object):
    """ 用来实现从 redis中获取队列 """
    queue_name = None
    redis_queue_key = None
    task_id = None

    redis_batch_size = 1
    redis_encoding = None

    # 获取IP地址
    local_ip = get_network('inet')

    logger = logger

    # Redis client placeholder.
    server = None

    def start_requests(self):
        """Returns a batch of start requests from redis."""
        return self.next_requests()

    def setup_redis(self, crawler=None):
        """Setup redis connection and idle signal.

        This should be called after the spider has set its crawler object.
        """
        if self.server is not None:
            return

        if crawler is None:
            # We allow optional crawler argument to keep backwards
            # compatibility.
            # XXX: Raise a deprecation warning.
            crawler = getattr(self, 'crawler', None)

        if crawler is None:
            raise ValueError("crawler is required")

        settings = crawler.settings

        if not (self.task_id and self.queue_name):
            raise ValueError("task_id queue_name must not be empty")

        self.redis_queue_key = "{}:{}".format(self.task_id, self.queue_name)

        try:
            self.redis_batch_size = int(self.redis_batch_size)
        except (TypeError, ValueError):
            raise ValueError("redis_batch_size must be an integer")

        if self.redis_encoding is None:
            self.redis_encoding = settings.get('REDIS_ENCODING', defaults.REDIS_ENCODING)

        self.logger.info("Reading start URLs from redis redis_queue_key '%(redis_queue_key)s' "
                         "(batch size: %(redis_batch_size)s, encoding: %(redis_encoding)s",
                         self.__dict__)

        self.server = RedisQueue(crawler.settings)
        # The idle signal is called when the spider has no requests left,
        # that's when we will schedule new requests from redis queue
        crawler.signals.connect(self.spider_idle, signal=signals.spider_idle)

    def next_requests(self):
        """ 这个函数的作用是生成下一匹次的URL """

        for i in range(self.redis_batch_size):
            # 移除队列，同时移动到运行中的队列中
            data = self.server.move_pop(
                key1=self.redis_queue_key,
                key2="{}:run:{}".format(self.redis_queue_key, self.local_ip)
            )

            # 队列为空
            if not data:
                break
            req = self.make_request_from_data(data)
            if req:
                yield req
            else:
                self.logger.debug("Request not made from data: %r", data)

    def make_request_from_data(self, data):
        """ 对数据的编码进行处理，返回 make_requests_from_url
        """
        url = bytes_to_str(data, self.redis_encoding)
        return self.make_requests_from_url(url)

    def schedule_next_requests(self):
        """ 调度获取下一次的请求 """
        for req in self.next_requests():
            self.crawler.engine.crawl(req, spider=self)

    def spider_idle(self):
        """Schedules a request if available, otherwise waits."""
        # XXX: Handle a sentinel to close the spider.
        # 把运行中的数据移动到处理好的结果处
        self.server.move_all(
            key1="{}:run:{}".format(self.redis_queue_key, self.local_ip),
            key2="{}:result:{}".format(self.redis_queue_key, self.local_ip)
        )
        self.schedule_next_requests()  # 获取下一次请求
        raise DontCloseSpider


class RedisQueueSpider(QueueMixin, Spider):
    """Spider that reads urls from redis queue when idle.
    """

    @classmethod
    def from_crawler(self, crawler, *args, **kwargs):
        obj = super(RedisQueueSpider, self).from_crawler(crawler, *args, **kwargs)
        obj.setup_redis(crawler)
        return obj


class RedisQueueCrawlSpider(QueueMixin, CrawlSpider):
    """Spider that reads urls from redis queue when idle.
    """

    @classmethod
    def from_crawler(self, crawler, *args, **kwargs):
        obj = super(RedisQueueCrawlSpider, self).from_crawler(crawler, *args, **kwargs)
        obj.setup_redis(crawler)
        return obj
