# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='scrapy_queue',
    version='0.1.0',
    description=(
        '这个项目是仿照 scrapy-redis 的一个包，用于构建分布式 scrapy 爬虫'
    ),
    long_description=open('README.rst').read(),
    author='parker',
    author_email='i54605@outlook.com',
    maintainer='parker',
    maintainer_email='i54605@outlook.com',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/parker-pu/scrapy_queue',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'scrapy',
        'psutil',
        'redis',
        'mmh3',
    ],
)
