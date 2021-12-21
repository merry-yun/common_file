#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2021-09-15 11:08
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2021-09-15 11:08
 * @Desc: common
'''
import time

from common.selelogin.utils.seleniums.webdriver import Browser


if __name__ == '__main__':
    # opt_kw = dict(
    #     driver_name="phantomjs", # 驱动类型 chrome/phantomjs/firefox
    #     headless=False, # 是否无头
    #     executable_path=r"G:\tmp\phantomjs-2.1.1-windows\phantomjs-2.1.1-windows\bin\phantomjs.exe", # 驱动路径
    #     disable_image=True, # 是否禁止图片渲染
    #     user_agent=None, # 自定义ua
    #     download_path=None, # 自动下载默认文件路径
    #     disable_popup=True, # 是否禁止弹窗
    #     load_extension=None, # 加载chrome插件路径
    #     proxy_service=None, # 代理服务地址 127.0.0.1:8888
    #     window_size=None, # 浏览器窗口大小
    #     remote_debugger_address=None, # 开启debugger地址 127.0.0.1:45631
    #     binary_location=None # 加载的本地exe二进制文件路径 该路径无法与沙箱一起使用
    # )
    opt_kw = dict(
        driver_name="chrome",
        headless=False,
        # window_size=(1920,1080),
        executable_path=r"G:/tmp/chromedriver_win32/chromedriver.exe",
        disable_image=True,  # 是否禁止图片渲染
        user_agent=None,  # 自定义ua
        download_path=None,  # 自动下载默认文件路径
        disable_popup=True,  # 是否禁止弹窗
        load_extension=None,  # 加载chrome插件路径
        proxy_service=None,  # 代理服务地址 127.0.0.1:8888
        window_size=None,  # 浏览器窗口大小
        remote_debugger_address=None,  # 开启debugger地址 127.0.0.1:45631
        binary_location=None  # 加载的本地exe二进制文件路径 该路径无法与沙箱一起使用
    )
    # opt_kw = dict(
    #     driver_name="firefox",
    #     headless=False,
    #     executable_path=r"C:\Users\zhanming.zhang\Downloads\geckodriver-v0.26.0-win64\geckodriver.exe"
    # )
    browser = Browser(**opt_kw)
    window = browser.execute_browser()
    with window as driver :
         driver.get("https://www.baidu.com")
         time.sleep(10)
    # 等同下列代码
    driver = window.driver
    driver.get("https://www.baidu.com")
    time.sleep(10)
    driver.quit()


