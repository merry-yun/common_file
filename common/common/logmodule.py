# -*- coding: utf-8 -*-

import os
import logging
from logging.handlers import TimedRotatingFileHandler
import time

def save_log_setting(dirpath, filename, level=logging.INFO):
    """
    记录日志设置
    :param dirpath: str, 日志文件存储位置
    :param filename: str, 日志文件名称
    :param level: 日志文件记录level, default: logging.INFO
    """
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    logging.basicConfig(level=level, filename=os.path.join(dirpath, filename), filemode='a', datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s %(pathname)s[line:%(lineno)d] %(levelname)s: %(message)s')


def save_log_setting_time(dirpath, filename, when='D', interval=1, backupCount=14, level=logging.INFO):
    """
    时间流转记录
    :param dirpath:目录
    :param filename:文件名
    :param when:指定日志文件轮转的时间单位
    :param interval:指定日志文件轮转的周期，如 when='S', interval=10，表示每10秒轮转一次，when='D', interval=7，表示每周轮转一次。
    :param backupCount:指定日志文件保留的数量，指定一个整数，则日志文件只保留这么多个，自动删除旧的文件。
    :param level:通知等级
    :return:
    """
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    logger = logging.getLogger(__name__)
    logger.setLevel(level=level)
    formatter = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s'
    time_rotate_file = TimedRotatingFileHandler(filename=os.path.join(dirpath, filename),
                                                when=when, interval=interval, backupCount=backupCount)
    time_rotate_file.setFormatter(logging.Formatter(formatter))
    time_rotate_file.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level=logging.INFO)
    console_handler.setFormatter(logging.Formatter(formatter))

    logger.addHandler(time_rotate_file)
    logger.addHandler(console_handler)


