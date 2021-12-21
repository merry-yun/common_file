#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2021/2/18 18:06
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2021/2/18 18:06
 * @Desc: common
'''

from zope.interface import Interface


class BaseSecurity(Interface):

    def decrypt(self, s): pass

    def encrypt(self, s): pass
