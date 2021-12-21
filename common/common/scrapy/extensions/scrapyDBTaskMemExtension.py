#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2020/9/9 15:05
 * @Last Modified by:   zhanming.zhang
 * @Last Modified time: 2020/9/9 15:05
 * @Desc: alibaba_s
任务打点
'''
import socket
import scrapy.signals
import sqlalchemy
import logging
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


class TmMarketTaskMemExtension:
    mem_name = "tm_market_task_mem"

    @classmethod
    def from_crawler(cls, crawler):
        o = cls()
        assert "TASK_MEM_NAME" in crawler.settings, "缺少 TASK_MEM_NAME 在settings中. 请在settings指定TASK_MEM_NAME的参数值"
        crawler.signals.connect(o.spider_closed, signal=scrapy.signals.spider_closed)
        return o

    def __gen_sql(self, cookie_id):
        ip = socket.gethostbyname(socket.gethostname())
        sql = "update %s set gmt_finish=NOW(),task_status='complete',executor='%s',cookie_id='%s' where id in ({})"
        return sql % (self.mem_name, ip, cookie_id)

    def spider_closed(self, spider):

        settings = spider.crawler.settings
        if settings.get("DEBUG_MODE") and settings.get("TESTDSN"):
            engine = sqlalchemy.create_engine(settings.get("TESTDSN"))
        else:
            engine = sqlalchemy.create_engine(settings.get("DSN"))
        self.mem_name = settings["TASK_MEM_NAME"]

        session = sessionmaker(bind=engine)()

        ids = []
        if hasattr(spider, "complete_tasks"):
            if isinstance(spider.complete_tasks, (tuple, list, set)):
                ids = list(spider.complete_tasks)
            else:
                logger.error("读取完成任务失败 原因已完成的任务列表 应该为spider的complete_tasks属性")
                return

        spider.logger.info(msg="获取已完成任务记录 len %d" % len(ids))
        if len(ids) > 0:
            if len(ids) == 1:
                ids.append(ids[0])
            sql = self.__gen_sql(cookie_id=spider.cookiesid).format(",".join(ids))
            logger.debug("update sql : " + sql)
            session.execute(sql)
            session.commit()
