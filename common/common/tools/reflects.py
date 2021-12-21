#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2021-09-22 14:30
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2021-09-22 14:30
 * @Desc: common
'''
import os
import sys
import time

import common
import jinja2
from common.tools.db.mysql.factory import Factory


def parse_cmdline_args_todict(args):
    cmdline = [
        "--scheme",
        "--table",
        "--write-select-sql"
    ]
    args = args[1:]
    assert len(args) % 2 == 0, "参数长度应为2的倍数"
    args_dict = dict()
    for i in range(0, len(args), 2):
        if args[i] not in cmdline:
            raise ValueError("命令行参数 不合法 应为 --scheme 或者 --table 或者 --write-select-sql")
        args_dict[args[i]] = args[i + 1]
    assert "--table" in args_dict, "--table 必要参数 但是你给了空值"
    return args_dict


def initDB(obj):
    if os.environ.get("COMMON_DSN") is None:
        raise ValueError("没有设置COMMON_DSN变量 程序错误退出")
    obj.db = Factory.from_settings(settings=dict(DSN=os.environ.get("COMMON_DSN")))


class TmplateCreateInstance:

    def __init__(self, packloader):
        self.packloader = packloader
        self.db = None

    @classmethod
    def from_settings(self):
        templates = os.path.abspath(os.path.join(common.__path__[0], "templates"))
        print("寻找模板路径", templates)
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates))
        return self(packloader=env)

    def _parse_item_args_from_db(self, scheme, table):
        if self.db is None:
            initDB(self)
        result = self.db.output_table_struct(scheme or "", table)
        return result

    def createItem(self, *args):
        args_dict = parse_cmdline_args_todict(sys.argv[1:])
        is_sql = False
        print(args_dict)
        if args_dict.get("--write-select-sql"):
            is_sql = True
        if not is_sql:
            tpl = self.packloader.get_template("scrapy_item_template.tpl")
            filename = "%s_item.py"
        else:
            tpl = self.packloader.get_template("select_item_template.tpl")
            filename = "%s_select.sql"

        d = self._parse_item_args_from_db(scheme=args_dict.get("--scheme"), table=args_dict["--table"])
        d["USER"] = os.environ.get("USERNAME")
        d["NOWTIME"] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time()))
        table = d["table"][0]
        table["name"] = table["name"].replace("-", "_")
        table["TABLENAME"] = "".join(list(map(lambda x: x.capitalize(), table["name"].split("_"))))
        d.pop("table")
        d["table"] = table
        result = tpl.render(**d)

        self.output_file(source=result, filename= filename % d["table"]["name"])

    def output_file(self, source, filename):
        if os.path.exists(filename):
            raise PermissionError("该文件已在路径下存在 %s" % filename)
        with open(filename, "wb") as fp:
            fp.write(source.encode())


if __name__ == '__main__':
    tp = TmplateCreateInstance.from_settings()
    tp.createItem()
