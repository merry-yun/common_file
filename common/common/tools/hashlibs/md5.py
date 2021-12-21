#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2020/9/22 16:20
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2020/9/22 16:20
 * @Desc: common
'''

from hashlib import md5


class Md5:

    def __init__(self):
        self.m = md5()

    def encrypt(self, s: bytes):
        self.m.update(s)
        return self

    def hex(self):
        return self.m.hexdigest()
