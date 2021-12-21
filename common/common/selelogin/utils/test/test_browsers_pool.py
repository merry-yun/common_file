#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2021-09-15 11:19
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2021-09-15 11:19
 * @Desc: common
'''
import queue
import random
import time

from common.selelogin.utils.seleniums.webdriver_pool import WebDriverPool

if __name__ == '__main__':
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
    driver_pool = WebDriverPool(pool_size=2,
                                recycle_mintue=30,
                                min_driver_count=0,
                                **opt_kw)

    url = "https://www.baidu.com/s?wd={}"
    keywords = [
        "iphone", "huawei", "xiaomi", "oppo", "vivo"
    ]

    for i in range(2):
        drivers = []
        for i in range(10):
            try:
                driverCallable = driver_pool.get(-1)
                drivers.append(driverCallable)
                print("获取浏览器实例", i)
            except queue.Empty as e:
                print("队列为空 无任何浏览器实例", i)

        for d in drivers:
            driver = d().driver
            driver.get(url.format(random.choice(keywords)))
        time.sleep(10)
        for d in drivers:  # 放回队列中
            driver_pool.put(d)
        del drivers
    # 按时间清理
    driver_pool.pong()
    # 全部关闭
    print(driver_pool.pool.qsize(), not driver_pool.pool.empty())
    driver_pool.close()
