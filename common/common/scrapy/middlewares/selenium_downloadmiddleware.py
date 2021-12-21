#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2021-09-15 16:46
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2021-09-15 16:46
 * @Desc: common
'''
import inspect
import logging

import scrapy.signals
from twisted.python.threadpool import ThreadPool
from common.scrapy.spiders.request import RenderRequest
from twisted.internet import reactor, threads
from scrapy.http.request import Request
from scrapy.http.response import Response

# from common.selelogin.utils.seleniums.webdriver import Browser
from common.selelogin.utils.seleniums.webdriver_pool import WebDriverPool
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


class SeleniumDownloadMiddleware:

    @classmethod
    def from_crawler(cls, crawler):

        settings = crawler.settings
        selenium_pool_size = settings.getint("SELENIUM_POOL_SIZE", 1)
        selenium_driver = settings.get("SELELNIUM_DRIVER", "phantomjs").lower()
        selenium_executable_path = settings.get("SELENIUM_EXECUTABLE_PATH", None)
        selenium_headless = settings.getbool("SELENIUM_HEADLESS")
        selenium_opt_kwargs = settings.get("SELENIUM_KWARGS")
        selenium_recycle_minute = settings.getint("SELENIUM_RECYCLE_MINUTE", 30)
        selenium_min_driver_count = settings.getint("SELENIUM_MIN_DRIVER_COUNT", 0)

        selenium_opt_kwargs["driver_name"] = selenium_driver
        selenium_opt_kwargs["headless"] = selenium_headless
        selenium_opt_kwargs["executable_path"] = selenium_executable_path

        if selenium_pool_size < 2:
            logger.info("指定的selenium pool size < 2 所以选择单个browser实例对象")
            drivers = WebDriverPool.from_settings(
                pool_size=1,
                recycle_mintue=selenium_recycle_minute,
                min_driver_count=1,
                **selenium_opt_kwargs
            )
        else:
            logger.info("指定的selenium pool size >= 2 所以选择多个browser实例对象")
            drivers = WebDriverPool.from_settings(
                pool_size=selenium_pool_size,
                recycle_mintue=selenium_recycle_minute,
                min_driver_count=selenium_min_driver_count,
                **selenium_opt_kwargs
            )
        thread_size = 32 if drivers.pool.maxsize * 2 > 32 else drivers.pool.maxsize * 2
        o = cls(drivers=drivers, thread_size=thread_size)

        crawler.signals.connect(o.spider_closed, signal=scrapy.signals.spider_closed)
        return o

    def __init__(self, drivers: WebDriverPool, thread_size: int):
        self._drivers = drivers
        self._threadpool = ThreadPool(1, thread_size)

    def process_request(self, request, spider):
        if not isinstance(request, RenderRequest):
            return

        if not self._threadpool.start():
            self._threadpool.start()

        # 参考线程池， 通过线程池获取浏览器驱动请求
        return threads.deferToThreadPool(
            reactor,
            self._threadpool,
            self.render_download,
            request, spider
        )

    def render_download(self, request, spider):

        if not request.url.startswith("https://") and not request.url.startswith("http://"):
            logger.error("请求并非标准的网络连接 应包含https:// or http:// 而不是 %s" % request.url)
        driver_callable = self._drivers.get(-1)
        driver = driver_callable().driver
        driver.get(request.url)
        if request.wait_until:
            WebDriverWait(driver, request.wait_timeout).until(request.wait_until)
        if request.script_js:
            try:
                request.meta["js_result"] = driver.execute_script(request.script_js)
            except Exception as e:
                logger.error(e)
                request.meta["js_result"] = "null"

        if request.driver_callback:
            result = request.driver_callback(driver, request)
            if isinstance(result, (Request, Response)):
                self._drivers.put(driver_callable)
                return result

        response = Response(
            url=driver.current_url,
            body=driver.page_source.encode(),
            request=request,
        )
        self._drivers.put(driver_callable)
        return response

    def spider_closed(self):

        self._drivers.close()
        del self._drivers
        # if not self._threadpool.stop():
        self._threadpool.stop()
