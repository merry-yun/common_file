#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2021-09-13 15:23
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2021-09-13 15:23
 * @Desc: common
'''
import os
import queue
import threading
import time
import weakref
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.phantomjs.service import Service as PhantomJsService

from common.selelogin.utils.seleniums.webdriver import Browser


class _Service:

    def __init__(self, driver_name, executable_path, service):
        self.executable_path = executable_path
        self._service = service
        self.driver_name = driver_name

    @classmethod
    def from_settings(cls, settings):
        executable_path = settings["executable_path"]
        driver_name = settings["driver_name"].lower()
        if driver_name == "chrome":
            service = ChromeService(executable_path)
        elif driver_name == "firefox":
            service = FirefoxService(executable_path)
        elif driver_name == "phantomjs":
            service = PhantomJsService(executable_path)
        else:
            raise AttributeError("该驱动类型暂不支持 %s" % driver_name)
        return cls(service=service, driver_name=driver_name, executable_path=executable_path)

    def start(self):
        self._service.command_line_args()
        self._service.start()

    def stop(self):
        try:
            self._service.stop()
        except Exception as e:
            print("服务停止失败 %s" % self.executable_path)
        # os.system('taskkill /im {} /F'.format(self.executable_path.split("/")[-1]))


class WebDriverPool:

    def __init__(self, pool_size=1, recycle_mintue=30, min_driver_count=0, service: _Service = None, **opt_kw):
        self.pool = queue.Queue(maxsize=pool_size)

        self.driver_count = 0
        self.opt_kw = opt_kw
        self.rlock = threading.RLock()
        self.lock = threading.Lock()
        self.lru_driver = dict()
        self.used_driver = dict()
        self.has_driver = set([])
        self.recycle_mintue = recycle_mintue  # 循环检测浏览存活 该参数仅有在方法pong调用才有效
        self._min_driver_count = min_driver_count  # 最小保证存活的个数
        self._service = service

    @classmethod
    def from_settings(self, **kw):

        # _service = _Service.from_settings(settings=opt_kw)
        # _service.start()
        _service = None
        return self(service=_service, **kw)

    def __del__(self):
        self.close()

    def close(self):
        while not self.pool.empty():
            driver = self.pool.get()
            try:
                self.remove(driver)
            except Exception as e:
                print("关闭浏览器实例失败 原因 %s" % e)
        time.sleep(3)

    def get(self, timeout: int = 5):

        if not self.is_full:
            with self.rlock:
                if not self.is_full:
                    opt_kw = self.opt_kw.copy()
                    driver = Browser(**opt_kw).start_browser()
                    self.pool.put(driver)
                    self.lru_driver[id(driver)] = int(time.time())
                    self.driver_count += 1
        if timeout > 0:
            driver = self.pool.get(timeout=timeout)
        else:
            driver = self.pool.get_nowait()
        print("获取浏览器实例 id: %d" % id(driver))
        self.lru_driver[id(driver)] = int(time.time())
        self.used_driver[id(driver)] = driver
        if id(driver) in self.has_driver:
            self.has_driver.remove(id(driver))
        return weakref.ref(driver)  # 调用driver方式 ()

    def put(self, driver):
        if isinstance(driver, weakref.ref):
            driver = driver()
        print("放回浏览器实例 id: %d" % id(driver))
        if self.pool.qsize() < self.driver_count:
            driver_id = id(driver)
            if self.used_driver[driver_id] and driver_id not in self.has_driver:
                self.pool.put(driver)
            if driver_id in self.lru_driver:
                self.lru_driver.pop(driver_id)
            self.has_driver.add(driver_id)
        else:
            self.remove(driver)
            return

    def remove(self, driver):
        if isinstance(driver, weakref.ref):
            driver = driver()

        print("删除浏览器实例 id: %d" % id(driver))
        driver.quit()
        # driver.close()
        driver_id = id(driver)
        if driver_id in self.lru_driver:
            self.lru_driver.pop(driver_id)
        if driver_id in self.used_driver:
            self.used_driver.pop(driver_id)
        if driver_id in self.has_driver:
            self.has_driver.remove(driver_id)
        del driver
        self.driver_count -= 1

    @property
    def is_full(self):
        return self.driver_count >= self.pool.maxsize

    def pong(self):

        with self.lock:
            st = int(time.time())
            qsize = self.pool.qsize()
            for _ in range(qsize):
                driver = self.get(-1)
                driver_id = id(driver)
                if driver_id in self.lru_driver and st - self.lru_driver[driver_id] > self.recycle_mintue * 60:
                    print("浏览器实例过期 id: %d" % id(driver))
                    self.remove(driver)
                # elif driver_id not in self.lru_driver:
                #     print("浏览器实例过期 id: %d" % id(driver))
                #     self.remove(driver)
                else:
                    print("浏览器实例未过期 id: %d" % id(driver))
                    self.put(driver)

            dids = tuple(self.used_driver.keys())
            for did in dids:
                driver = self.used_driver[did]
                if did in self.lru_driver and st - self.lru_driver[did] > self.recycle_mintue * 60:
                    print("浏览器实例过期解除引用 id: %d" % id(did))
                    print("浏览器实例过期 id: %d" % did)
                    if driver is None:
                        self.used_driver.pop(did)
                        self.lru_driver.pop(did)
                    else:
                        self.remove(driver)

        assert self._min_driver_count < 30, "人为设置最小的阈值 < 30"
        if self.pool.qsize() < self._min_driver_count:
            for i in range(self._min_driver_count - self.pool.qsize()):
                driver = self.get()
                self.put(driver)
