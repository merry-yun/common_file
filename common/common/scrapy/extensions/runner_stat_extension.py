#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2021-09-26 14:35
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2021-09-26 14:35
 * @Desc: common
 取代scrapy自带的CoreStats

'''
from scrapy.extensions.corestats import CoreStats
from scrapy.utils.trackref import format_live_refs


class RunnerCoreStats(CoreStats):

    def spider_closed(self, spider, reason):
        super(RunnerCoreStats, self).spider_closed(spider=spider, reason=reason)
        if hasattr(spider, "msg_collect") and isinstance(spider.msg_collect, list):
            stats = self.stats._stats.copy()
            if hasattr(spider, "_task_id_"):
                stats["_task_id_"] = spider._task_id_
            if hasattr(spider, "cookiesid"):
                stats["cookiesid"] = spider.cookiesid
            stats["live_refs"] = format_live_refs()
            spider.msg_collect.append(
                stats
            )
