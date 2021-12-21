#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2021/5/10 16:25
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2021/5/10 16:25
 * @Desc: common
'''

"""
负责查询每个scrapy项目下的spider参数情况
搜寻结果
tbn参数 代表 表格名称 匹配 xx_tbn tbn_xxx tbn 模块
name参数 代表spider的名称ID
urls参数 脚本中的url匹配
comment参数 第一个的 三双引号 注释内容

"""

import os
import re
import pprint


class Checker:
    register_sql = None
    register_sql_update = None

    def spiders_checker(self, bot_name: str, spider_paths: list):
        """
        bot_name scrapy的项目名称
        spider_paths spider路径，传入列表
        """
        comment = re.compile('"""([\n\s\w\W]+?)"""')
        tbn = re.compile("tbn = .([a-zA-Z0-9\_]+)")
        https = re.compile("(http\S+?\w.com/?)")
        name = re.compile("name = .([a-zA-Z0-9\_]+)")
        for spider_pth in spider_paths:
            files = os.listdir(spider_pth)
            for file in files:
                if not file.endswith("py") or file.startswith("__"):
                    continue
                py_file = os.path.join(spider_pth, file)
                with open(py_file, "rb") as fp:
                    py_content = fp.read().decode("utf8", errors="ignore")
                c = comment.search(py_content)
                t = tbn.findall(py_content)
                h = set(https.findall(py_content))
                n = name.search(py_content)
                df = dict()
                df["script"] = file
                if n:
                    df["spider_name"] = n.group(1)
                    # print(file, t)
                else:
                    df["spider_name"] = ''

                if c:
                    df["comment"] = c.group(0).replace('"""', "").strip()
                    # print(file, c.group(0))
                else:
                    df["comment"] = ""
                if t:
                    df["tables"] = set(t) - set(["kwargs", "tbn", "wargs", "bn"])
                    if len(df["tables"]) == 0:
                        df["tables"] = ["", ]
                else:
                    df["tables"] = ["", ]
                df["urls"] = "\n".join(h)

                for result in df['tables']:
                    item = df
                    item['tables'] = result.replace("\'", "")
                    item['bot_name'] = bot_name
                    yield item

    def spider_register_path(self,
                             item: dict,
                             conn: object,
                             tablename: str = None,
                             sql_mode: int = 2):
        """
        sql_mode 0 仅插入 1 更新并插入
        """
        import sqlalchemy
        if tablename is None:
            tablename = "spider_taowai.remind_platforms_path_mapping"
        if sql_mode == 1:
            sql = f"REPLACE INTO {tablename}(`comment`, script, spider_name, tables, urls,bot_name) VALUES " \
                  "(:comment, :script, :spider_name, :tables, :urls,:bot_name)"
        else:
            sql = f"INSERT IGNORE INTO {tablename}(`comment`, script, spider_name, tables, urls,bot_name) VALUES " \
                  "(:comment, :script, :spider_name, :tables, :urls,:bot_name)"
        sql = sqlalchemy.text(sql)
        data = dict(comment=item['comment'].replace(">", "-"),
                    script=item['script'],
                    spider_name=item['spider_name'],
                    tables=item['tables'],
                    bot_name=item['bot_name'],
                    urls=item['urls'].replace("%3A", ":").replace("%2F", "/"))
        if conn is not None:
            # print(sql, data)
            conn.execute(sql, data)
        else:
            print(sql , data)

    def spider_register_url(self,
                             item: dict,
                             conn: object,
                             tablename: str = None,
                             sql_mode: int = 2):
        """
        sql_mode 0 仅插入 1 更新并插入
        """
        import sqlalchemy
        if tablename is None:
            tablename = "spider_taowai.remind_platforms_url_mapping"
        if sql_mode == 1:
            sql = f"REPLACE INTO {tablename}(bot_name, url) VALUES " \
                  "(:bot_name, :url)"
        else:
            sql = f"INSERT IGNORE INTO {tablename}(bot_name, url) VALUES " \
                  "(:bot_name, :url)"
        sql = sqlalchemy.text(sql)
        data = dict(bot_name=item['bot_name'], url=item['url'].replace("%3A", ":").replace("%2F", "/"))
        if conn is not None:
            conn.execute(sql, data)
        else:
            print(sql , data)

    def spider_register_urls(self,
                             item: dict,
                             conn: object,
                             tablename: str = None,
                             sql_mode: int = 2):
        _item_url = []
        for url in item.get('urls').split("\n"):
            _item_url.append(dict(bot_name=item['bot_name'], url=url))
        for item in _item_url:
            self.spider_register_url(item=item, conn=conn, tablename=tablename, sql_mode=sql_mode)

    def spider_split_cookiesid(self, conn, sql=None, sql_insert=None):

        if conn is None:
            print("conn 参数应该是一个 sqlalchemy.create_engine 对象 而不是 None")
            return conn

        if sql is None:
            sql = """
                select bot_name , spider_name , kw , finish_time from spider_taowai.remind_spider_logstat rsl where 1=1
                and create_date > DATE(NOW()-INTERVAL 2 DAY)
                order by id desc
                """
        if sql_insert is None:
            import sqlalchemy
            sql_insert = """INSERT IGNORE INTO spider_taowai.remind_query_depences(bot_name,spider_name,table_name,cookiesid, register_time,source) 
            value (:bot_name,:spider_name,:table_name,:cookiesid, :register_time,:source)"""
            sql_insert = sqlalchemy.text(sql_insert)
            print(sql_insert)

        tbn = re.compile("tbn[^=]*=(.+?)[;$]")
        cookiesid = re.compile("c.*id=(.+?)[;$]")
        ret = conn.execute(sql)
        items = []
        for q in ret.fetchall():
            # print(q)
            tables = tbn.findall(q.kw) or ['', ]
            cookiesids = cookiesid.findall(q.kw) or ['', ]
            for table in tables:
                for cook in cookiesids:
                    if re.search("ali|jd|pdd", cook):
                        cook = cook.split("_")[0]

                    if table.startswith("f_"):
                        source = "客服专用库"
                    else:
                        source = "爬虫专用库"

                    items.append(
                        dict(bot_name=q.bot_name,
                             spider_name=q.spider_name,
                             table_name=table.replace("`", ""),
                             cookiesid=cook,
                             register_time=q.finish_time,
                             source=source)
                    )
        print(len(items))
        conn.execute(sql_insert, items)




    def illegal_table_name(self, tablename):
        pass



