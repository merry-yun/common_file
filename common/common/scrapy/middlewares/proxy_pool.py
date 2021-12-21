#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2021/6/9 16:34
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2021/6/9 16:34
 * @Desc: common
'''
import logging
import os
import random

import scrapy.utils.python
import scrapy.utils.response
from scrapy.downloadermiddlewares.retry import RetryMiddleware


class ProxyPool:
    _conn = None

    def __init__(self, conn):
        self._conn = conn

    @classmethod
    def new(cls, url):
        import redis
        _conn = redis.Redis.from_url(url=url, decode_responses=True)
        return cls(conn=_conn)

    def queryAll(self) -> list:
        args = self._conn.execute_command("hgetall", "proxy:ip")
        if args is None:
            return []
        return args


logger = logging.getLogger(__name__)


class ProxyPoolDownloadMiddleWare(RetryMiddleware):
    """
    继承基类 增加进行代理重试
    """

    cache_proxy_pool = None  # 集合 set([])

    def __init__(self, settings, proxy_pool):
        super(ProxyPoolDownloadMiddleWare, self).__init__(settings=settings)
        self._proxy_pool = proxy_pool

    @classmethod
    def start_server(cls):
        print("若使用PROXY_CLASS 非REDIS模式 则这里必须实现你的代理获取")
        print("开始你的代理服务 必须实现 queryAll() -> []string")

    @classmethod
    def from_crawler(cls, crawler):
        proxy_clazz = crawler.settings.get("PROXY_CLASS")
        if proxy_clazz is None or proxy_clazz.upper() == "REDIS":
            redis_url = crawler.settings.get("PROXY_REDIS_URL")
            env_redis_url = os.getenv("PROXY_REDIS_URL")
            if env_redis_url is not None and redis_url and redis_url.find("10.2.0.9") > -1:
                raise ValueError("代理地址已经更新 更新最新的代理地址")
            elif env_redis_url:
                redis_url = env_redis_url
            server = ProxyPool.new(
                url=redis_url or "redis://@127.0.0.1:6379/0"
            )
        else:
            server = cls.start_server()
        return cls(settings=crawler.settings, proxy_pool=server)

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = scrapy.utils.response.response_status_message(response.status)
            return self.retry(request, reason, spider) or response
        return response

    def retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1

        retry_times = self.max_retry_times

        if 'max_retry_times' in request.meta:
            retry_times = request.meta['max_retry_times']

        stats = spider.crawler.stats
        if retries <= retry_times:
            logger.debug("Retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})
            if retries >= 2:
                if "proxy" in request.meta:
                    self.remove_proxy(proxy=request.meta['proxy'])

            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            if not self.is_inter_ip(url=request.url):
                retryreq.meta['proxy'] = self.proxy_one()
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust

            if isinstance(reason, Exception):
                reason = scrapy.utils.python.global_object_name(reason.__class__)

            stats.inc_value('retry/count')
            stats.inc_value('retry/reason_count/%s' % reason)
            return retryreq
        else:
            stats.inc_value('retry/max_reached')
            logger.debug("Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})

    def process_request(self, request, spider):
        if not self.is_inter_ip(url=request.url):
            request.meta['proxy'] = self.proxy_one()

    def proxy_one(self):
        if self.cache_proxy_pool is None or len(self.cache_proxy_pool) == 0:
            self.refresh_proxy()
        p = random.sample(self.cache_proxy_pool, 1)[0]
        if isinstance(p, bytes):
            p = p.decode()
        logger.debug("get proxy %s" % p)
        return p

    def is_inter_ip(self, url):
        if url.find("//10.") > 0 or url.find("//172.") > 0 or url.find("//127.") > 0:
            return True
        return False

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
                and not request.meta.get('dont_retry', False):
            return self.retry(request, exception, spider)


    def refresh_proxy(self):
        logger.debug("refresh proxy cache")
        self.cache_proxy_pool = {"https://%s" % i for i in self._proxy_pool.queryAll()}

    def remove_proxy(self, proxy):
        logger.debug("remove proxy %s" % proxy)
        try:
            if proxy in self.cache_proxy_pool:
                self.cache_proxy_pool.remove(proxy)
        except KeyError:
            pass