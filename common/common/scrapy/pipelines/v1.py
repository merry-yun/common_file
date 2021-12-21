#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2020/6/24 9:40
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2020/6/24 9:40
 * @Desc: jd_s_re
'''
import logging

from twisted.enterprise import adbapi
import re
import pymysql
from urllib.parse import unquote_plus
"""
使用方式
正常导入scrapy pipeline的方式 
同时spider配置sql属性

"""


class ShopCommentsPipeline:

    def __init__(self, pool):

        self.db_pool = pool

    @classmethod
    def from_settings(cls, settings):
        """
        全局对象
        :param settings:
        :return:
        """
        print('SELECTED_DSN', settings['SELECTED_DSN'])
        if settings.get("SELECTED_DSN") and settings.get(settings.get("SELECTED_DSN")):
            logging.info("设置特定的数据库连接 %s" % settings.get("SELECTED_DSN"))
            dsn = settings[settings.get("SELECTED_DSN")]
        elif settings.get('DEBUG_MODE', False):
            if 'TESTDSN' in settings:
                dsn = settings['TESTDSN']
                logging.debug("Found TESTDSN , Select TESTDSN")
            else:
                dsn = settings['DSN']
                logging.debug("No found TESTDSN , Select DSN")
        else:
            dsn = settings['DSN']

        params = re.search("//(.*?):(.*)@(.*?):(\d*?)/(.*?)\?", dsn)
        db_kw = dict(
            host=params.group(3),
            port=int(params.group(4)),
            db=params.group(5),
            user=params.group(1),
            passwd=unquote_plus(params.group(2)),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        db_pool = adbapi.ConnectionPool('pymysql', **db_kw)

        return cls(pool=db_pool)

    def process_item(self, item, spider):

        result = self.db_pool.runInteraction(self.insert, item, spider)
        result.addErrback(errback=self.error, item=item)

        return item

    def error(self, reason, item):
        logging.error(item)
        # _item = tuple(map(lambda x: x[1], sorted(item.items(), key=lambda x: x[0])))
        # logging.error(self.update_sql % item)
        logging.error(reason)

    def insert(self, cursor, item, spider):

        sql = spider.sql

        _item = tuple(map(lambda x: x[1], sorted(item.items(), key=lambda x: x[0])))

        cursor.execute(sql, _item)
