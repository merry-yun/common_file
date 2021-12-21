#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2021/4/29 10:16
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2021/4/29 10:16
 * @Desc: common

 common工具盒 - 时间模块
'''

import re
import datetime
import time


class TimeStrPattern:
    day = re.compile("(\d+)天")
    hour = re.compile("(\d+)小时")
    minute = re.compile("(\d+)分钟")
    second = re.compile("(\d+)秒")


def _search(pattern, src_str):
    _st = pattern.search(src_str)
    if _st is None:
        return 0
    else:
        return int(_st.group(1))


def ZhTimeStrToStandard(src_str, unit='min'):
    """
    将 xx天xx小时**分钟zz秒 转成标准时间戳或者指定单位的数值
    :param src_str:
    :param unit:
    :return:
    """
    seconds = 0
    seconds += _search(TimeStrPattern.day, src_str) * 60 * 60 * 24
    seconds += _search(TimeStrPattern.hour, src_str) * 60 * 60
    seconds += _search(TimeStrPattern.minute, src_str) * 60
    seconds += _search(TimeStrPattern.second, src_str)
    if unit == 'hour':
        return round(seconds / 3600, 4)
    elif unit == 'sec':
        return round(seconds / 1, 4)
    elif unit == 'min':
        return round(seconds / 60, 4)
    else:
        return round(seconds / 60, 4)


def TimeNow(zone: int):
    """
    获取当地时间，切勿使用datetime.datetime.now()获取时间。该方法是获取当前服务器时区的时间
    一旦遇到主从服务器时区不一致会导致时间异常
    :param zone:
    :return:
    """
    t = datetime.datetime.utcnow() + datetime.timedelta(hours=zone)
    return t.strftime("%Y-%m-%d %H:%M:%S")


def DateNow(offset_day=0, zone=0):
    """
    与TimeNow一致 获取指定时区的和偏移的时间日期
    :param offset_day:
    :param zone:
    :return:
    """
    n = datetime.datetime.utcnow()
    if zone != 0:
        n = n + datetime.timedelta(hours=zone)
    if offset_day == 0:
        n = n - datetime.timedelta(days=offset_day)
    return n.strftime("%Y-%m-%d")


def dateTotemp(date):
    """
    将字符串date转化为时间戳
    :param date:
    :return:temp
    """
    timeArray = time.strptime(date, "%Y-%m-%d %H:%M:%S")
    temp = int(time.mktime(timeArray))
    return temp

def tempTodate(temp):
    """
    将时间戳转化为时间格式【年-月-日】
    :param temp:
    :return:
    """
    date = time.localtime(temp)
    date = time.strftime("%Y-%m-%d", date)
    return date

# 以下是北京时间获取方法
BeijingTimeNow = lambda: TimeNow(8)
BeijingDateNow = lambda: DateNow(0, 8)
BeijingDateYesterDay = lambda: DateNow(1, 8)
BeijingDateTomorrow = lambda: DateNow(-1, 8)
