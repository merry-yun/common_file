#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2020/6/24 15:51
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2020/6/24 15:51
 * @Desc: common - 定义节点结构体
'''


class Node:

    def __init__(self, name, value, type, parent=None):

        self.field = name.lower() if name else name
        self.value = value
        self.type = type
        self.parent = parent
