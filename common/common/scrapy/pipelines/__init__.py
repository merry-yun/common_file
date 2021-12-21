#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2020/9/22 15:59
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2020/9/22 15:59
 * @Desc: common
'''

import logging
import re

import pymysql
import twisted.enterprise.adbapi

from common.scrapy.pipelines.v1 import ShopCommentsPipeline as MySQLInsertPipeline
from common.scrapy.pipelines.v2 import MySQLPipeline as MySQLUpdateOrInsertPipeline
from common.scrapy.pipelines.v3 import MultiPipelines as MultiItemsPipelines
from common.scrapy.pipelines.v4 import LogConsolePipeline


"""
使用方式
ITEM_PIPELINES = {
   'common.scrapy.pipelines.MySQLInsertPipeline': 300, # 只增不更新
   'common.scrapy.pipelines.MySQLUpdateOrInsertPipeline': 300, # 检查更新
    'common.scrapy.pipelines.MultiItemsPipelines': 300, # 多个item在pipelines分类插入
}
"""
