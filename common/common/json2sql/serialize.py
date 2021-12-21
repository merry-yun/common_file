#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2020/6/24 15:55
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2020/6/24 15:55
 * @Desc: common - 开始序列化json
'''
import datetime
import sys
import json

import jsonpath
from common.json2sql.node import Node
from common.json2sql.create import generateCreateSQL
from common.json2sql.create import CREATE_TABLE_BEGIN, CREATE_TABLE_END, FIELD_FOR_UPDATE

class Json2SQL:

    stack = []
    sql = ''


    def decode(self, body, tbn, suffix=None, with_prefix=False,  *pks):
        """
        body: dict or list object
        tbn: table name
        suffix: extra fields
        with_prefix: create field name with its parent name
        pks: primary keys
        """
        self.with_prefix = with_prefix
        self.__serialize(body=body, tbn_prefix=tbn, suffix=suffix, *pks)


    def to_file(self, tbn):
        if self.sql :
            with open(tbn + "_structure.sql", "w", encoding="utf8") as fp:
                fp.write(self.sql)


    def __serialize(self, body, tbn_prefix, suffix, *args):

        cur = body
        stack = sorted(list(cur.keys()))
        for k in stack:
            self.stack.append(Node(name=k, value=cur[k], type=type(cur[k])))

        tbn = tbn_prefix+ "_main"
        s = CREATE_TABLE_BEGIN % tbn
        fields = []
        while len(self.stack) > 0:
            kk = self.stack.pop(0)
            if kk.type == 0:
                print("获取字段定义: " , fields)
                fields = []
                _comment = input("输入表格`%s`备注: " % tbn).strip()
                if suffix is not None:
                    s += suffix
                s += CREATE_TABLE_END % (",".join(args), _comment)

                print(s)
                _save_file = input("是否导出SQL结构文件(y/n): ").strip().lower()
                if _save_file == 'y':
                    self.sql += "\n\n\n-- 生成时间：%s\n" % datetime.datetime.now()
                    self.sql += s
                print("\n")
                tbn = tbn_prefix + "_" + kk.field
                s = CREATE_TABLE_BEGIN % tbn
                continue

            if kk.type == dict:
                cur = kk.value
                stack = sorted(list(cur.keys()))
                for k in stack:
                    n = kk.field+"_"+k if self.with_prefix else k
                    self.stack.insert(0, Node(name=n, value=cur[k], type=type(cur[k])))

            if kk.type == list and len(kk.value) > 0 and isinstance(kk.value[0], dict):
                self.stack.append(Node(name=kk.field, value=0, type=0))
                cur = kk.value[0]
                stack = sorted(list(cur.keys()))
                for k in stack:
                    self.stack.append(Node(name=k, value=cur[k], type=type(cur[k]), parent=kk.field))

            fields.append(kk.field)
            s += generateCreateSQL(node=kk)
            # print(s)


if __name__ == '__main__':
    jq = Json2SQL()
    suffix = "`thedate` date DEFAULT NULL COMMENT '日期',\n" \
          "`updatetime` datetime(0) NULL DEFAULT NULL COMMENT '更新時間',\n" \
          "`inserttime` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '插入時間',\n" \
          "`cookiesid` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '帐号',\n"
    pks = ("cookiesid", "thedate")
    jq.decode(body=json.load(open("test.json", encoding="utf8", errors="ignore")), suffix=suffix, tbn="test")
    jq.to_file(tbn="test")



