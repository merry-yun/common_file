#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2021-09-22 15:33
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2021-09-22 15:33
 * @Desc: common
'''

import sqlalchemy


class Factory:

    def __init__(self, engine):
        self._engine = engine

    @classmethod
    def from_settings(cls, settings):
        engine = sqlalchemy.create_engine(settings["DSN"].strip('"'))
        return cls(engine)

    def output_table_struct(self, scheme, table) -> dict:
        column_sql = f"select COLUMN_NAME , COLUMN_COMMENT , COLUMN_TYPE, COLUMN_KEY from information_schema.`COLUMNS` c where TABLE_NAME = \"{table}\""
        if scheme:
            column_sql += f" AND TABLE_SCHEMA='{scheme}'"
        table_sql = f"SELECT TABLE_NAME , TABLE_SCHEMA , ifnull(TABLE_COMMENT,'') AS TABLE_COMMENT FROM information_schema.TABLES t WHERE TABLE_NAME = \"{table}\""
        column_result = self._engine.execute(column_sql).fetchall()
        table_result = self._engine.execute(table_sql).fetchone()
        column_result_dict = []
        table_result_dict = []
        for cr in column_result:
            column_result_dict.append(
                dict(name=cr.COLUMN_NAME, comment=cr.COLUMN_COMMENT, type=cr.COLUMN_TYPE, key=cr.COLUMN_KEY))
        table_result_dict.append(
            dict(name=table_result.TABLE_NAME, scheme=table_result.TABLE_SCHEMA, comment=table_result.TABLE_COMMENT))
        return dict(fields=column_result_dict, table=table_result_dict)


if __name__ == '__main__':
    s = Factory.from_settings(
        settings=dict(DSN="mysql+pymysql://root:data@wpz24wtl@172.18.114.3:3306/spider_tmall?charset=utf8mb4"))
    ss = s.output_table_struct("", "sycm_tmall_marco")
    print(ss)
