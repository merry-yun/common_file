#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''


 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2021-09-17 14:25
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2021-09-17 14:25
 * @Desc: common
'''

import sys
from common.tools.reflects import TmplateCreateInstance


class Manager:

    def welcome(self):
        screen = '''
Hello, 你的命令参数不存在喔~

    -- by ys.spider
'''
        print(screen)

    def genitem(self):
        print("开始映射 数据库进行item生成")
        tpl = TmplateCreateInstance.from_settings()
        tpl.createItem()


def execute():
    manager = Manager()
    if sys.argv[1] == "genitem":
        manager.genitem()
    else:
        manager.welcome()


if __name__ == '__main__':
    execute()