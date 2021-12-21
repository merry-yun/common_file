#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2020/9/22 15:41
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2020/9/22 15:41
 * @Desc: common
python 脚本登录模块base cls
使用方法
from common.selelogin import BaseLoginAbstract

class XxLogin(BaseLoginAbstract):

    def __execute_login(self):
        # todo: 在此实现你自己的登录方法
        pass

XxLogin.fromsetings(**setings)

'''


class BaseLoginAbstract:

    def __init__(self, username, password, target_url, login_url):
        self.username = username
        self.password = password
        self.login_url = login_url
        self.target_url = target_url

    def login(self, retry=0):
        assert isinstance(retry, int) and retry > 0, "{retry} 取值应大于等于0的整数  你输入的类型值是 %r" % retry
        for _ in range(retry):
            self.__execute_login()

    def __execute_login(self):
        raise NotImplementedError

    @classmethod
    def fromsettings(cls, **settings):
        o = cls(username=settings['username'],
                password=settings['password'],
                target_url=settings['target_url'],
                login_url=settings['login_url'])
        return o.login(retry=settings.get("retry", 0))
