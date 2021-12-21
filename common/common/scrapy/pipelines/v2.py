#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2020/9/4 10:55
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2020/9/4 10:55
 * @Desc: douyin_s
'''

from common.scrapy.pipelines.v1 import ShopCommentsPipeline


class MySQLPipeline(ShopCommentsPipeline):
    select_sql = None
    update_sql = None

    def insert(self, cursor, item, spider):

        self.__update_or_insert(cursor=cursor, item=item, spider=spider)

    def __update_or_insert(self, cursor, item, spider):
        cursor.execute(self.get_select_sql(tbn=spider.tbn, primary_keys=spider.primary_keys) % item)
        result = cursor.fetchone()
        if result:
            spider.logger.debug("数据已存在 现进行更新数据")
            spider.logger.debug(item)
            cursor.execute(self.get_update_sql(tbn=spider.tbn, primary_keys=spider.primary_keys, item=item) % item)
        elif spider.sql_mode == "insert_or_update":
            _item = tuple(map(lambda x: x[1], sorted(item.items(), key=lambda x: x[0])))
            cursor.execute(spider.sql, _item)

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
        where = " AND ".join(["{0}='%({0})s'".format(pk) for pk in primary_keys])
        fields = ",".join(
            ["{0}='%({0})s'".format(i) for i in filter(lambda x: x if x not in primary_keys else None, item.keys())])
        self.update_sql = f"UPDATE {tbn} SET {fields} WHERE {where}"
        return self.update_sql
