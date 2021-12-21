#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2021-09-15 16:36
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2021-09-15 16:36
 * @Desc: common
'''

from scrapy.spiders import Request as _Request


class RenderRequest(_Request):
    """
    负责通过中间渲染

    """

    def __init__(self, url,
                 callback=None,
                 headers=None,
                 cookies=None,
                 meta=None,
                 errback=None,
                 flags=None,
                 cb_kwargs=None,
                 wait_timeout=30,
                 script_js=None,
                 driver_callback=None,
                 wait_util=None):

        self._timeout = wait_timeout
        self._script = script_js
        self.driver_callback = driver_callback #这个是传入 driver, request进行操作
        super(RenderRequest, self).__init__(url=url,
                                            callback=callback,
                                            method='GET',
                                            headers=headers,
                                            cookies=cookies,
                                            meta=meta,
                                            errback=errback,
                                            flags=flags,
                                            cb_kwargs=cb_kwargs,
                                            dont_filter=True
                                            )
        self.wait_until = wait_util # 这个是一个传入driver对象 返回true/false的函数

    def driver_callback(self, driver, spider):
        pass


    @property
    def script_js(self):
        return self._script

    @property
    def wait_timeout(self):
        return self._timeout
