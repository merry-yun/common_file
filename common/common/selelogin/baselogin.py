#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2020/9/22 15:25
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2020/9/22 15:25
 * @Desc: common
 定义浏览器base cls
 所有的浏览器方法统一属性方法仅能如下几种
 若是需要定制某渠道的浏览器操作 通过继承或者组合该base cls进行功能拓展
'''
import time

import random
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
"""
实例方法
from common.selelogin import BaseLoginMixin as BaseLogin
settings = {
    "username":"xxx",
    "password":"xxx",
    "firefox_or_chrome": "f"/"c" firefox/chrome
}
BaseLogin.fromsettings(**settings)
"""


class BaseLoginMixin(object):
    handles_list = list()  # 句柄列表

    def __init__(self, username, password, login_url, target_url, profile=None, fc='f'):
        """
        初始化
        :param username: str, 账号,
        :param password: str, 密码,
        :param login_url: str, 登录链接
        :param target_url: str, 登录成功后跳转的链接
        :param profile: 浏览器配置,
        :param fc: str,
            'f' - firefox浏览器
            'c' - chrome浏览器
        """
        self.username = username
        self.password = password
        self.login_url = login_url
        self.target_url = target_url
        if fc == 'f':
            self.browser = webdriver.Firefox(firefox_profile=profile)
        elif fc == 'c':
            self.browser = webdriver.Chrome(options=profile, executable_path=r"C:\Users\zhanming.zhang\Downloads\chromedriver_win32\chromedriver.exe")
        self.browser.implicitly_wait(5)
        self.__wait = WebDriverWait(self.browser, 5)

    @staticmethod
    def _base642img(src_url):
        """
        base64转img
        :param src_url: str, like: 'data:image/png;base64, iVBORw0KGg...'
        :return: img,
        """
        pass

    @staticmethod
    def _url2img(src_url):
        """
        url转img
        :param src_url: str,
        :return: img,
        """
        pass

    @staticmethod
    def _format_style(style_str):
        """
        解析字符串, 获得html标签的style属性
        :param style_str: str,
        :return: dict,
        """
        pass

    def _click_by_xpath(self, element_xpath):
        """
        根据xpath, 点击指定元素
        :param element_xpath: str, 待点击元素xpath
        :return:
            True - 元素存在, 操作完成
            False - 元素不存在, 操作失败
        """
        try:
            element_click = self.__wait.until(EC.presence_of_element_located((By.XPATH, element_xpath)))
            element_click.click()
        except Exception:
            logging.warning('click_by_xpath fail, can not find: %s' % element_xpath)
            return False
        return True

    def _input_by_xpath(self, keys, input_xpath, delay=True):
        """
        根据xpath, 在输入框输入对应keys
        :param keys: str, 待输入关键词
        :param input_xpath: str, 输入框xpath
        :param delay: bool, 是否延时
        :return:
            True - 元素存在, 操作完成
            False - 元素不存在, 操作失败
        """
        try:
            element_input = self.__wait.until(EC.presence_of_element_located((By.XPATH, input_xpath)))
            element_input.clear()
            if delay is True:
                for ehchar in keys:
                    time.sleep(random.choice([0.2, 0.3, 0.4]))
                    element_input.send_keys(ehchar)
            else:
                element_input.send_keys(keys)
        except Exception:
            logging.warning('input_by_xpath fail, can nat find: %s' % input_xpath)
            return False
        return True

    def _slide_by_xpath(self, element_xpath, x, y):
        """
        根据xpath, 拖动元素到指定位置
        :param element_xpath: str, 待拖动元素
        :param x: str, 指定位置x
        :param y: str, 指定位置y
        :return:
            True - 元素存在, 操作完成
            False - 元素不存在, 操作失败
        """
        try:
            slice_btn = self.__wait.until(EC.presence_of_element_located((By.XPATH, element_xpath)))
        except Exception:
            return False
        else:
            # slice_btn.click()
            ActionChains(self.browser).click_and_hold(slice_btn).perform()
            time.sleep(0.5)
            tmp = int(x / 2)
            ActionChains(self.browser).move_by_offset(xoffset=tmp, yoffset=y).perform()
            time.sleep(0.5)
            ActionChains(self.browser).move_by_offset(xoffset=int(x - tmp), yoffset=y).perform()
            time.sleep(0.5)
            ActionChains(self.browser).move_by_offset(xoffset=5, yoffset=0).perform()
            time.sleep(0.5)
            ActionChains(self.browser).move_by_offset(xoffset=-5, yoffset=0).perform()
            time.sleep(0.5)
            ActionChains(self.browser).release().perform()
        return True

    def _roll2foot(self):
        """
        慢慢滚动至页面底部
        """
        for eh in range(1, 16):
            self.browser.execute_script('window.scrollTo(0, parseInt(document.body.scrollHeight / 15 * %d))' % eh)
            time.sleep(0.5)

    def rool2foot(self):
        self._roll2foot()

    def click_by_xpath(self, element_xpath):
        return self._click_by_xpath(element_xpath)

    def input_account(self):
        """
        输入账号密码
        :return:
        """
        pass

    def pass_captcha(self):
        """
        通过验证码, 包括滑块验证码, 图片验证码, 等
        :return:
        """
        pass

    def login(self, retry=None):
        """
        登录流程
        :param retry: int, 登录失败时的重试次数
        :return:
        """
        # 跳转到对应链接
        # 选择登录(如有)
        # 切换iframe(如有)
        # 切换密码登录(如有)
        # 输入账号密码
        # 点击登录按钮
        # 通过验证
        # 如没通过验证, 重试验证, 重试次数用尽, 返回False
        # 如通过验证, 返回True
        pass

    def chk_url(self, url=None):
        """
        检查当前url是否为指定url
        :param url: str, 指定连接, 若为None则为target_url
        :return:
            True - 已跳转到指定连接
            False - 未跳转到指定连接
        """
        time.sleep(2)
        if url is None:
            url = self.target_url
        url_curr = self.browser.current_url
        if url_curr.startswith(url):  # 如登录成功, 返回True
            logging.info('chk_url success')
            return True
        # 如登录失败, 返回False
        logging.warning('chk_url fail')
        return False

    def get_cookies(self):
        """
        获取当前页面cookies
        :return: dict,
        """
        cookies = self.browser.get_cookies()
        return cookies

    def close(self):
        self.browser.close()
        self.browser.quit()

    def slide_block_by_xpath(self, slider_xpath, slider_bg_xpath, release=True):
        """
        滑块验证, 前提是要切换到对应页面/iframe, 除了登录还会用在其他地方
        :param slider_xpath: str, 滑块xpath
        :param slider_bg_xpath: str, 滑块背景xpath
        :param release: bool, 拖动滑块后是否释放, True - 释放, False - 不释放
        :return:
            True - 滑动成功
            False - 滑动失败
        """
        # 滑块操作
        try:
            slider = self.__wait.until(EC.visibility_of_element_located((By.XPATH, slider_xpath)))  # 滑块是否可见
            slider_bg = self.__wait.until(EC.presence_of_element_located((By.XPATH, slider_bg_xpath)))
        except Exception as err:
            return False
        else:
            slider_bg_width = int(slider_bg.size['width'])
            ActionChains(self.browser).click_and_hold(slider).perform()
            time.sleep(0.5)
            ActionChains(self.browser).move_by_offset(xoffset=100, yoffset=0).perform()
            time.sleep(0.5)
            ActionChains(self.browser).move_by_offset(xoffset=50, yoffset=0).perform()
            time.sleep(0.5)
            ActionChains(self.browser).move_by_offset(xoffset=slider_bg_width - 150, yoffset=0).perform()
            time.sleep(0.5)
            if release is True:
                # ActionChains(self.browser).move_by_offset(xoffset=slider_bg_width, yoffset=0).perform()
                ActionChains(self.browser).release().perform()
        return True

    def add_handle(self, url, addad=True):
        """
        新建标签页, 用于抢不同投放位置的广告位
        :param url:
        :param addad: bool, 是否加入到handles_ad列表中
        :return:
        """
        js = 'window.open("%s")' % url
        self.browser.execute_script(js)
        handles_all = self.browser.window_handles
        self.browser.switch_to.window(handles_all[-1])
        handle_now = self.browser.current_window_handle
        if addad is True:
            self.handles_list.append(handle_now)

    def remove_handle(self, handle):
        """
        关闭句柄，并在抢广告位专用句柄中删除对应句柄
        :param handle: str, 句柄
        """
        # 切换到指定句柄
        self.browser.switch_to.window(handle)
        time.sleep(1)
        # 删除(从浏览器中删除标签页, 从handles_ad中删除句柄)
        self.browser.close()
        self.handles_list.remove(handle)
        # 默认切换回最后的标签页
        handle_all = self.browser.window_handles
        self.browser.switch_to.window(handle_all[-1])

    def to_bottom(self):
        """
        移动到页面底部
        """
        self.browser.execute_script('window.scrollTo(0, parseInt(document.body.scrollHeight))')
        time.sleep(0.5)

    @classmethod
    def fromsettings(cls, **settings):

        o = cls(username=settings['username'],
                password=settings['password'],
                login_url=settings['login_url'],
                target_url=settings['target_url'],
                profile=settings['profile'],
                fc=settings['firefox_or_chrome'])
        return o.login(retry=settings.get("retry", False))
