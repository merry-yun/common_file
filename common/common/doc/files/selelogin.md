# 登录插件

包含两个基类

```
from common.selelogin.utils.seleniums.webdriver import Browser # 这是一个单浏览器实例类
from common.selelogin.utils.seleniums.webdriver_pool import WebDriverPool # 这是自己实现的一个线程安全浏览器池

# 测试实例可以参考下的方法
from common.selelogin.utils.seleniums.test import test_single_browser # 这是一个测试单浏览器实例类
from common.selelogin.utils.seleniums.test import test_browsers_pool # 这是自己实现的一个线程安全的测试浏览器池

```

输入参数

```
 # -- test_single_browser
 opt_kw = dict(
        driver_name="chrome",
        headless=False,
        # window_size=(1920,1080),
        executable_path=r"chromedriver.exe",
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
    #     executable_path=r"geckodriver.exe"
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
```

# 登录基类 baselogin.py

定义浏览器base cls
 所有的浏览器方法统一属性方法仅能如下几种
 若是需要定制某渠道的浏览器操作 通过继承或者组合该base cls进行功能拓展

```
实例方法
from common.selelogin import BaseLoginMixin as BaseLogin
settings = {
    "username":"xxx",
    "password":"xxx",
    "firefox_or_chrome": "f"/"c" firefox/chrome
}
BaseLogin.fromsettings(**settings)
```