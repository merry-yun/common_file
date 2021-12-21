#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2020/12/22 13:37
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2020/12/22 13:37
 * @Desc: common
'''

import logging
from common.security.rsa import RsaSecurity
from scrapy import signals
import datetime
import sqlalchemy
import os
import socket
import psutil

logger = logging.getLogger(__name__)


def delete_pgspider_30d_ago(pg_engine):
    sql = "DELETE FROM public.bdp_spider_process_log_30d WHERE create_date < date(now() + interval '-30 DAY')"
    try:
        pg_engine.execute(sql)
    except Exception as e:
        logger.error("删除PG爬虫信息日志记录 失败  原因:%s" % e)


class LogStatUpdateExtension:
    """
    收集爬虫采集信息上传到服务器数据库
    """

    def __init__(self, stats, watcher, bot_name):
        self.stats = stats
        self.watcher = watcher
        self.bot_name = bot_name

    @classmethod
    def from_crawler(cls, crawler):
        stats = crawler.stats
        watcher = crawler.settings.get("LOG_WATCHER")
        o = cls(stats, watcher, crawler.settings.get("BOT_NAME"))
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        return o

    def spider_opened(self, spider):
        if not isinstance(self.watcher, str) or not self.watcher.startswith("mysql"):
            logger.warning("[%s] 开启数据日志收集服务 失败" % spider.name)
            logger.warning("[%s] 失败原因 LOG_WATCHER 参数类型应为`str`, 而不是`%s` 或 前缀应包含mysql+pymysql://*" %
                           (spider.name, type(self.watcher)))
        else:
            logger.info("[%s] 开启数据日志收集服务 成功" % spider.name)

    def spider_closed(self, spider, reason):

        if not isinstance(self.watcher, str) or not self.watcher.startswith("mysql"):
            return
        logger.info("[%s] 关闭爬虫进程 收集数据准备上传信息" % spider.name)
        self.stats.set_value("bot_name", self.bot_name)
        self.stats.set_value("spider_name", spider.name)

        constant = dir(spider)
        not_constant = ("sql", "name", "__module__")
        s = ""
        for f in constant:
            getattr_f = getattr(spider, f)
            if isinstance(getattr_f, (int, float, str)) and f not in not_constant:
                s = "{}={}; {}".format(f, getattr(spider, f), s)
        s = s.strip()

        stats_dict = self.stats._stats
        _stats = {
            "process_id": os.getpid(),
            "host": socket.gethostname(),
            "bot_name": stats_dict["bot_name"],
            "spider_name": stats_dict["spider_name"],
            "finish_reason": stats_dict["finish_reason"],
            "finish_time": str(stats_dict["finish_time"]),
            "start_time": str(stats_dict["start_time"]),
            "item_scraped_count": stats_dict.get("item_scraped_count", -1),
            "request_bytes": stats_dict.get("downloader/request_bytes", -1),
            "request_count": stats_dict.get("downloader/request_count", -1),
            "request_method_get": stats_dict.get("downloader/request_method_count/GET", -1),
            "request_method_post": stats_dict.get("downloader/request_method_count/POST", -1),
            "request_depth_max": stats_dict.get("request_depth_max", -1),
            "response_bytes": stats_dict.get("downloader/response_bytes", -1),
            "response_count": stats_dict.get("downloader/response_count", -1),
            "response_received_count": stats_dict.get("response_received_count", -1),
            "response_200": stats_dict.get("downloader/response_status_count/200", -1),
            "response_302": stats_dict.get("downloader/response_status_count/302", -1),
            "response_404": stats_dict.get("downloader/response_status_count/404", -1),
            "elapsed_time_seconds": stats_dict.get("elapsed_time_seconds", -1),
            "log_debug": stats_dict.get("log_count/DEBUG", -1),
            "log_info": stats_dict.get("log_count/INFO", -1),
            "log_warning": stats_dict.get("log_count/WARNING", -1),
            "log_error": stats_dict.get("log_count/ERROR", -1),
            "deq_count": stats_dict.get("scheduler/dequeued", -1),
            "deq_memory": stats_dict.get("scheduler/dequeued/memory", -1),
            "enq_count": stats_dict.get("scheduler/enqueued", -1),
            "enq_memory": stats_dict.get("scheduler/enqueued/memory", -1),
            "ip": "",
            "kw": s
        }
        process = psutil.Process(os.getpid())
        # mem = round(process.memory_info().rss / 1024 / 1024, 2)  # MB
        _stats['process_mem_rss'] = round(process.memory_info().rss / 1024 / 1024, 2) #　MB
        _stats['process_cpu_percent'] = process.cpu_percent()

        _stats["ip"] = socket.gethostbyname(_stats["host"])
        _stats_tuple = tuple(_stats.items())

        fields = ",".join(map(lambda x: x[0], _stats_tuple))
        values = "'" + "','".join(map(lambda x: str(x[1]), _stats_tuple)) + "'"
        self.report_spider_db(fields=fields, values=values)
        self.report_bdp_pgspider_table(fields=fields, values=values)

    def split_table(self, conn, tbn):
        """
        增加分表操作 按条数切割或者按日期切割
        """

        # 按日期切割表
        dt = datetime.datetime.now()
        if dt.day == 1 and dt.month in (7, 1):
            # 在 1月和 7月的时候切割表格 半年度归档
            exist_table = "SELECT count(table_name) FROM information_schema.TABLES " \
                          "WHERE table_name = '%s'"
            logger.info(exist_table % "o_{}_{}".format(tbn, dt.strftime("%Y%m%d")))
            ret = conn.execute(exist_table % "o_{}_{}".format(tbn, dt.strftime("%Y%m%d"))).fetchall()
            if ret[0][0] == 0:
                rename_table = "alter table %s rename to o_%s_%s" % (tbn, tbn, dt.strftime("%Y%m%d"))
                logger.info(rename_table)
                conn.execute(rename_table)

            ret = conn.execute(exist_table % tbn).fetchall()
            if ret[0][0] == 0:
                create_table = "create table %s like o_%s_%s" % (tbn, tbn, dt.strftime("%Y%m%d"))
                logger.info(create_table)
                conn.execute(create_table)

    def report_spider_db(self, fields, values):
        """
        汇总爬虫库
        """
        sql = "INSERT INTO remind_spider_logstat(%s,create_time, create_date) value (%s,NOW(), DATE(NOW()))" % (
            fields, values)
        try:

            engine = sqlalchemy.create_engine(self.watcher)
            self.split_table(conn=engine, tbn="remind_spider_logstat")
            engine.execute(sql)
            logger.info("上传信息至爬虫库 成功")
        except Exception as e:
            logger.error("上传信息至爬虫库 失败.  原因: %s" % e)

    def report_bdp_pgspider_table(self, fields, values):
        """
        汇报中台 调度系统库
        """
        PG_LOG_WATCHER = "PG_LOG_WATCHER"
        PGRSAPATH = "PGRSAPATH"
        if not os.getenv(PGRSAPATH):
            logger.error("PGRSAPATH 缺失 请设置PGRSAPATH环境变量进行私钥解密")
            return
        if not os.getenv(PG_LOG_WATCHER):
            logger.error("PG_LOG_WATCHER 缺失")
            return

        pg_url = os.getenv(PG_LOG_WATCHER)
        if pg_url and pg_url.startswith("V21"):
            _ = os.getenv(PGRSAPATH)
            if _ is None:
                logger.error("PGRSAPATH 缺失 请设置PGRSAPATH环境变量进行私钥解密")
                return
            private_path = os.path.abspath(os.path.join(os.getenv(PGRSAPATH), "pg_private.pem"))
            if not os.path.exists(private_path):
                logger.error("PGRSAPATH 不存在 请设置PGRSAPATH环境变量进行私钥解密")
                return
            rsa = RsaSecurity.new(private=private_path)
            pg_url = rsa.decrypt(pg_url)

        sql = "INSERT INTO public.bdp_spider_process_log_30d(%s,create_time, create_date,task_type) values (%s,NOW(), " \
              "DATE(NOW()),'CRAWL')" % (
                  fields, values)
        try:
            dbengine = sqlalchemy.create_engine(pg_url, echo=False, client_encoding='utf8')
            dbengine.execute(sql)
            delete_pgspider_30d_ago(pg_engine=dbengine)
            logger.info("上传信息至PG调度系统库 成功")
        except Exception as e:
            logger.error("上传信息至PG调度系统库 失败.  原因: %s" % e)
