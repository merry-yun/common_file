#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2020/11/16 16:44
 * @Last Modified by:   zhanming.zhang
 * @Last Modified time: 2020/11/16 16:44
 * @Desc: oversea_s
针对一个spider多个items类进行分类解析
'''
import logging
from common.scrapy.pipelines.basic import AdbAPIConnectionPool


logger = logging.getLogger(__file__)

"""
# demo 插入或更新
class JztReportAdExtraPipeline(MultiPipelines):
    sql = None
    tbn = "jzt_reportad_extra"
    primary_keys = ('adid',)
    clazz_name = "JztReportadExtraItem"
    sql_mode = "insert_or_update"

# demo 插入
class JztReportAdExtraPipeline(MultiPipelines):
    sql = None
    tbn = "jzt_reportad_extra"
    primary_keys = None
    clazz_name = "JztReportadExtraItem"
    sql_mode = "insert"


"""


class MultiPipelines:
    select_sql = None
    update_sql = None

    # 进行表格参数初始化
    sql = None
    tbn = None
    primary_keys = None
    clazz_name = None
    sql_mode = ""

    def __init__(self, pool, stats):
        self.db_pool = pool
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        """
        全局对象
        :param settings:
        :return:
        """
        settings = crawler.settings
        if "SELECTED_DSN" in settings:
            dsn = settings.get(settings['SELECTED_DSN'])
        elif settings.get('DEBUG_MODE', False):
            if 'TESTDSN' in settings:
                dsn = settings['TESTDSN']
                logger.debug("Found TESTDSN , Select TESTDSN")
            else:
                dsn = settings['DSN']
                logger.debug("Not Found TESTDSN , Select DSN")
        else:
            dsn = settings['DSN']

        # db_pool = twisted.enterprise.adbapi.ConnectionPool('pymysql', **db_kw)
        adbapi = AdbAPIConnectionPool(dsn=dsn)
        adbapi.setDBPool()
        db_pool = adbapi.getDBPool()

        return cls(pool=db_pool, stats=crawler.stats)

    def process_item(self, item, spider):

        result = self.db_pool.runInteraction(self.insert, item, spider)
        result.addErrback(errback=self.error, item=item)

        return item

    def error(self, reason, item):
        logger.error(reason)
        if logger.isEnabledFor(logging.DEBUG):
            _item = tuple(map(lambda x: x[1], sorted(item.items(), key=lambda x: x[0])))
            logger.debug(self.sql % _item)
            logger.debug(self.update_sql % item)
        # print(self.sql % _item)
        # print(self.update_sql % item)

    def insert(self, cursor, item, spider):
        # print("insert", item, item.__class__.__name__, item.__class__.__name__ == self.clazz_name, self.clazz_name)
        if item and item.__class__.__name__ == self.clazz_name:
            self.stats.inc_value('item_scraped_count' + '/' + self.clazz_name)
            if self.sql is None:
                self.sql = self.gen_sql(tbn=self.tbn, keys=item.keys())
            self.update_or_insert(cursor=cursor,
                                  item=item,
                                  spider=spider,
                                  tbn=self.tbn,
                                  primary_keys=self.primary_keys,
                                  sql=self.sql)

    def update_or_insert(self, cursor, item, spider, tbn, primary_keys, sql):

        if self.sql_mode == "insert":
            _item = tuple(map(lambda x: x[1], sorted(item.items(), key=lambda x: x[0])))
            cursor.execute(sql, _item)
            return

        cursor.execute(self.get_select_sql(tbn=tbn, primary_keys=primary_keys) % item)
        result = cursor.fetchone()
        if result:
            spider.logger.debug("数据已存在 现进行更新数据")
            spider.logger.debug(item)
            cursor.execute(self.get_update_sql(tbn=tbn, primary_keys=primary_keys, item=item) % item)
        elif self.sql_mode == "insert_or_update":
            _item = tuple(map(lambda x: x[1], sorted(item.items(), key=lambda x: x[0])))
            cursor.execute(sql, _item)

    def get_select_sql(self, tbn, primary_keys):

        if self.select_sql is not None:
            return self.select_sql

        where = " AND ".join(["{0}=\"%({0})s\"".format(pk) for pk in primary_keys])
        fields = ",".join(primary_keys)
        self.select_sql = f"SELECT {fields} FROM {tbn} WHERE {where} LIMIT 1"
        return self.select_sql

    def get_update_sql(self, tbn, item, primary_keys):

        if self.update_sql is not None:
            return self.update_sql
        where = " AND ".join(["`{0}`='%({0})s'".format(pk) for pk in primary_keys])
        fields = ",".join(
            ["`{0}`='%({0})s'".format(i) for i in filter(lambda x: x if x not in primary_keys else None, item.keys())])
        self.update_sql = f"UPDATE {tbn} SET {fields} WHERE {where}"
        return self.update_sql

    def gen_sql(self, tbn, keys):
        """
        若使用PublicADBPipeline, 请在这里填写你的sql构造器
        """
        fields = "`" + "`,`".join(sorted(keys)) + "`"
        values = ",".join(['%s'] * len(keys))
        sql = f"INSERT IGNORE INTO {tbn}({fields}) values ({values})"
        return sql
