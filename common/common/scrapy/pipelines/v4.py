#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2021-09-13 14:20
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2021-09-13 14:20
 * @Desc: common
 LogConsole日志Pipline是将数据item保存持久化在日志文件中。因此需要和LOG_FILE配置一起使用。
 使用范围 满足下列三个条件
 1. 大规模数据的采集 规模是10万级以上
 2. 数据适合只增不更新不删除
 3. 配合日志解析脚本进行数据数据库的解析上传
'''

import copy
import logging
import json
import time
from base64 import b64encode


class LogConsolePipeline:

    logger = logging.getLogger(__name__)
    isDebug = None

    def process_item(self, item, spider):
        """
         LogConsole日志Pipline是将数据item保存持久化在日志文件中。因此需要和LOG_FILE配置一起使用。
         使用范围 满足下列三个条件
         1. 大规模数据的采集 规模是10万级以上
         2. 数据适合只增不更新不删除
         3. 配合日志解析脚本进行数据数据库的解析上传
        """
        if item is None:
            return
        item_ = dict(info=copy.deepcopy(item),
                     _data_type_=0,
                     _log_time_=None,
                     _tbn_=getattr(spider, "tbn", "undefine"))
        self.check_set_default_time(item=item_)
        if self.is_debug(spider=spider):
            self.logger.debug("返回item: %r" % item)
        else:
            self.log_item_to_console(item=item_)

    def is_debug(self, spider):
        if isinstance(self.isDebug, bool):
            return self.isDebug
        if spider.settings["LOG_LEVEL"] == "DEBUG":
            self.isDebug = True
        else:
            self.isDebug = False
        return self.isDebug

    def log_item_to_console(self, item):

        print("========json::%s::json========" % b64encode(json.dumps(item, ensure_ascii=False).encode()).decode())

    def check_set_default_time(self, item:dict):
        """
        该方法是传入item进行默认值修改
        """
        item["_log_time_"] = int(time.time())*1000
        item["_data_type_"] = 0

if __name__ == '__main__':
    t = LogConsolePipeline()
    for i in range(12):
        a = i * 9864
        t.process_item(dict(a=12,b=12,i=a), dict())