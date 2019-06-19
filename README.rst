scrapy-queue
==================

``scrapy-queue`` scrapy-redis is a similar library

Installation
------------

.. figure:: https://secure.travis-ci.org/selwin/python-user-agents.png
   :alt: Build status

   Build status

``scrapy-queue`` is hosted on
`PyPI <http://pypi.python.org/pypi/scrapy-queue/>`__ and can be installed
as such:

::

    pip install scrapy-queue

Alternatively, you can also get the latest source code from
Github_ and install it manually.

.. _Github: https://github.com/parker-pu/scrapy-queue

Usage
-----

Various basic information that can help you identify visitors can be
accessed ``RedisQueueSpider``,``RedisQueueCrawlSpider``, ``QueuePipeline``,``BloomFilter`` and ``RedisHashFilter`` attributes. For example:

.. code:: python


    pass

Currently these attributes are supported:

-  ``RedisQueueSpider``: redis queue Spider
-  ``RedisQueueCrawlSpider``: redis queue CrawlSpider
-  ``QueuePipeline``: scrapy Pipeline
-  ``BloomFilter``: bloom filter
-  ``RedisHashFilter``: redis hash filter

For example:

.. code:: python


    pass

Running Tests
-------------

::

    python -m unittest discover

Changelog
---------

Version 0.1.0
~~~~~~~~~~~

-  Initial release

Initialize code development
