#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2021/1/6 11:02
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2021/1/6 11:02
 * @Desc: common

 sql 导出文件
'''
import os
import logging

logger = logging.getLogger(__name__)


class FileXiaoer:

    def __init__(self, conn, filename):
        """
        conn: db connection like sqlalchemy.create_engine(dsn)
        filename: be saved filename
        """

        self._conn = conn
        self.filename = filename
        self._df = None
        self._read_sql_execute = None
        self._excel_writer = None
        self._default_run()

    def _default_run(self):
        import pandas
        self._read_sql_execute = pandas.read_sql
        self._excel_writer = pandas.ExcelWriter

    @property
    def data(self):
        return self._df

    def df_replace(self, df):
        self._df = df

    def execute(self, sql):

        self._df = self._read_sql_execute(sql, self._conn)

    def to_file(self):
        """
        若启动该函数 excel只会保存单个sheet。
        若想保存为多个sheet 启用to_excel_sheets
        """
        ext_file = self.filename.split(".")[-1]
        if ext_file == "csv":
            self._df.to_csv(self.filename, index=False)
        elif ext_file in ("xls", "xlsx"):
            self._df.to_excel(self.filename, index=False)
        elif ext_file == "json":
            self._df.to_json(self.filename)
        elif ext_file in ("htm", "html"):
            self._df.to_html(self.filename)
        else:
            logger.warning("文件后缀名不可识别 请确保是否是 csv/xls/xlsx/json/html/htm")
            return
        pwd = os.path.abspath(os.path.join(".", self.filename))
        logger.info("文件成功保存 路径为%s" % pwd)

    def to_dict(self):
        if self._df is not None:
            return self._df.to_dict()

    def to_excel_sheets(self, a):
        """
        a should be tuple/dict
        [(sheet1, sql1), (sheet2, sql2)] or
        {
            sheet1: sql1,
            sheet2: sql2
        }
        """
        if isinstance(a, dict):
            a = iter(a.items())

        ext_file = self.filename.split(".")[-1]
        if ext_file in ("xls", "xlsx"):
            to_file = "to_excel"
        else:
            logger.warning("文件后缀名不可识别 请确保是否是 xls/xlsx")
            return

        ew = self._excel_writer(self.filename)
        for sheet, sql in a:
            df = self._read_sql_execute(sql, self._conn)
            getattr(df, to_file)(ew, sheet, index=False)
        ew.save()
        pwd = os.path.abspath(os.path.join(".", self.filename))
        logger.info("文件成功保存 路径为%s" % pwd)

    def get_abs_path(self):
        pwd = os.path.abspath(os.path.join(".", self.filename))
        return pwd
