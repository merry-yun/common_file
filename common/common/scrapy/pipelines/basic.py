#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2021-09-13 14:45
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2021-09-13 14:45
 * @Desc: common
'''
import logging
import re

import pymysql
import twisted.enterprise.adbapi


class _singleton(type):
    _instance = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super(_singleton, cls).__call__(*args, **kwargs)
        return cls._instance[cls]


class ReconnectingMySQLConnectionPool(twisted.enterprise.adbapi.ConnectionPool):
    """
    This connection pool will reconnect if the server goes away.  This idea was taken from:
    http://www.gelens.org/2009/09/13/twisted-connectionpool-revisited/
    """
    def _runInteraction(self, interaction, *args, **kw):
        try:
            return twisted.enterprise.adbapi.ConnectionPool._runInteraction(self, interaction, *args, **kw)
        except pymysql.OperationalError as e:
            if e[0] not in (2006, 2013):
                raise pymysql.OperationalError
            conn = self.connections.get(self.threadID())
            self.disconnect(conn)
            return twisted.enterprise.adbapi.ConnectionPool._runInteraction(self, interaction, *args, **kw)


class AdbAPIConnectionPool(metaclass=_singleton):
    db_pool = None

    def __init__(self, dsn):
        self.dsn = dsn

    def setDBPool(self):
        if self.db_pool is None:
            logging.info("initializing db connection.....")
            params = re.search("//(.*?):(.*)@(.*?):(\d*?)/(.*?)\?", self.dsn)
            db_kw = dict(
                host=params.group(3),
                port=int(params.group(4)),
                db=params.group(5),
                user=params.group(1),
                passwd=params.group(2),
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor
            )

            self.db_pool = ReconnectingMySQLConnectionPool('pymysql', **db_kw)
        else:
            logging.info("return db connection......")

    def getDBPool(self):

        return self.db_pool

    def reloadDBPool(self):

        logging.info("reinitializing db connection.....")
        params = re.search("//(.*?):(.*)@(.*?):(\d*?)/(.*?)\?", self.dsn)
        db_kw = dict(
            host=params.group(3),
            port=int(params.group(4)),
            db=params.group(5),
            user=params.group(1),
            passwd=params.group(2),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )

        self.db_pool = twisted.enterprise.adbapi.ConnectionPool('pymysql', **db_kw)
        return self.db_pool