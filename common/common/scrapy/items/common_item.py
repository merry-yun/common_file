#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2020/9/22 16:00
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2020/9/22 16:00
 * @Desc: common
固定Item字段字段
'''

import scrapy


class CommonItem(scrapy.Item):


    cookiesid = scrapy.Field()
    inserttime = scrapy.Field()



