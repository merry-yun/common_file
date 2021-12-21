#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2021-09-13 15:23
 * @Last Modified by:   zhanming.zhang
 * @Last Modified time: 2021-09-13 15:23
 * @Desc: common
'''
import logging
import os
import traceback
import common
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class PhantomJSOptions:

    def __init__(self, service_args, dcap):
        self.service_args = service_args
        self.dcap = dcap


class Browser:
    driver_map = {
        "chrome": webdriver.Chrome,
        "firefox": webdriver.Firefox,
        "phantomjs": webdriver.PhantomJS
    }
    logger = logging.getLogger(__name__)

    def __init__(self, driver_name: str, executable_path, options=None, **opt_kw):
        assert driver_name.lower() in self.driver_map, f"{driver_name} 不在可实例化列表中"
        self.driver_name = driver_name.lower()
        self.executable_path = executable_path
        if options is None:
            self.options = _make_browser_from_settings(self.driver_name, **opt_kw)
        else:
            self.options = self.options
        self.window_size = opt_kw.get("window_size")

    def start_browser(self):
        kw = {
            "executable_path": self.executable_path,
            "options": self.options
        }
        if self.driver_name in ("firefox", "phantomjs"):
            kw["service_log_path"] = "nul"
        browserClass = self.driver_map[self.driver_name]
        if self.driver_name == "phantomjs":
            driver = browserClass(
                executable_path=self.executable_path,
                service_args=kw["options"].service_args,
                desired_capabilities=kw["options"].dcap,
                service_log_path="nul"
            )
        else:
            driver = browserClass(executable_path=self.executable_path,
                                  options=kw["options"],
                                  service_log_path="nul")
        if self.driver_name in ("firefox", "phantomjs") and self.window_size:
            driver.set_window_size(self.window_size[0], self.window_size[1])
        self.prepare_driver(driver)  # 删除浏览器指纹 以及 处理其他js操作
        return _WebDriver(driver=driver)

    execute_browser = start_browser

    def prepare_driver(self, driver):
        if isinstance(driver, webdriver.Chrome):
            """
             Object.defineProperty(
                    navigator, 'webdriver', {
                        get: ()=> undefined
                    }
                    )
            """
            self.logger.debug("perparing driver with executing some scripts")
            # 隐藏浏览器特征
            js = os.path.abspath(os.path.join(common.__file__, "../selelogin/utils/seleniums/js/browser_chief.js"))
            print("导入隐藏浏览器特征的js文件 路径 %s" % js)
            with open(js) as f:
                js = f.read()
            driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument", {
                    "source": js
                }
            )


def _make_browser_from_settings(driver_name,
                                headless=True,
                                disable_image=True,
                                user_agent=None,
                                download_path=None,
                                disable_popup=True,
                                load_extension=None,
                                proxy_service=None,
                                window_size=None,
                                remote_debugger_address=None,
                                binary_location=None,
                                **opt_kw):
    """
    driver_name驱动名称
    headless是否隐藏无头
    disable_image禁用图片渲染模式
    user_agent UA
    """
    if driver_name == "chrome":
        options = webdriver.ChromeOptions()
        options.headless = headless
        options.add_argument('--distable-gpu')
        if user_agent:
            options.add_argument(f"--user-agent={user_agent}")

        prefs = {
            # 'profile.managed_default_content_settings.images': 2,  # 不加载图片
            # 'profile.default_content_settings.popups': 0,  # 禁止弹窗
            # 'download.default_directory': download_dir,  # 下载到指定目录
        }

        if disable_image:
            prefs["profile.managed_default_content_settings.images"] = 2
        if disable_popup:
            prefs["profile.default_content_settings.popups"] = 0
        if download_path:
            prefs["download.default_directory"] = download_path
        if len(prefs) > 0:
            options.add_experimental_option("prefs", prefs)
        if load_extension:
            options.add_argument(f"load-extension={load_extension}")
        if proxy_service:
            if callable(proxy_service):
                options.add_argument("--proxy-service={}".format(proxy_service()))
            else:
                options.add_argument(f"--proxy-service={proxy_service}")
        if window_size:
            options.add_argument("--window-size={0},{1}".format(window_size[0], window_size[1]))
        if remote_debugger_address:
            options.debugger_address = remote_debugger_address
        if binary_location:
            options.binary_location = binary_location
        options.add_experimental_option("excludeSwitches", ["enable-automation", ])
        options.add_experimental_option("useAutomationExtension", False)
        # docker 里运行需要
        # options.add_argument("--no-sandbox")
        return options

    if driver_name == "firefox":
        options = webdriver.FirefoxOptions()
        profile = webdriver.FirefoxProfile()
        options.headless = headless
        options.add_argument("--disable-gpu")
        if disable_image:
            options.set_preference("permissions.default.image", 2)
        if user_agent:
            options.set_preference("general.useragent.override", user_agent)
        if binary_location:
            options.binary_location = binary_location

        if proxy_service:
            assert isinstance(proxy_service, str), "输入proxy_service变量类型应为str 而不是 %s 类型" % type(proxy_service)
            _ = urlparse(proxy_service)
            if _.scheme != "":
                proxy_service = _.netloc
            else:
                proxy_service = _.path,
            proxy_ip, proxy_port = proxy_service.split(":")
            profile.set_preference('network.proxy.type', 1)
            profile.set_preference('network.proxy.http', int(proxy_ip))
            profile.set_preference('network.proxy.http_port', proxy_port)
            profile.set_preference('network.proxy.ssl', int(proxy_ip))
            profile.set_preference('network.proxy.ssl_port', proxy_port)
            profile.set_preference("security.ssl3.dhe_rsa_aes_128_sha", False)
            profile.accept_untrusted_certs = True
            profile.set_preference("security.enterprise_roots.enabled", True)

        if disable_popup:
            print("Firefox 暂不支持该参数在初始化设置 disable_popup")
        if load_extension:
            print("Firefox 暂不支持该参数在初始化设置 load_extension")
        if remote_debugger_address:
            print("Firefox 暂不支持该参数在初始化设置 remote_debugger_address")
        if download_path:
            profile.set_preference("browser.download.folderList", 2)
            profile.set_preference("browser.download.dir", download_path)
            profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")

        if window_size:
            print("Firefox 暂不支持该参数在初始化设置 window_size")

        options.accept_insecure_certs = True
        options.profile = profile
        return options
    if driver_name == "phantomjs":
        import warnings
        warnings.filterwarnings("ignore")
        options = dict()
        dcap = DesiredCapabilities.PHANTOMJS
        if disable_image:
            options["load-images"] = "no"

        if user_agent:
            dcap["phantomjs.page.settings.userAgent"] = user_agent
        if binary_location:
            print("PhantomJS 暂不支持该参数在初始化设置 binary_location")

        if proxy_service:
            if callable(proxy_service):
                options["proxy"] = proxy_service()
            else:
                options["proxy"] = proxy_service

        if disable_popup:
            print("PhantomJS 暂不支持该参数在初始化设置 disable_popup")
        if load_extension:
            print("PhantomJS 暂不支持该参数在初始化设置 load_extension")
        if remote_debugger_address:
            assert isinstance(remote_debugger_address, str), "remote_debugger_address 而不是 %s 类型" % type(
                remote_debugger_address)
            _ = urlparse(remote_debugger_address)
            if _.scheme != "":
                debugger_service = _.netloc
            else:
                debugger_service = _.path
            debugger_port = int(debugger_service.split(":")[-1])
            options["remote-debugger-port"] = debugger_port

        if window_size:
            print("PhantomJS 暂不支持该参数在初始化设置 window_size")
        if "phantomjs_custom_settings" in opt_kw:
            custom_settings = opt_kw.pop("phantomjs_custom_settings")
            for setting in custom_settings:
                if setting.strip("-") in options:
                    print("PhantomJS 配置中已经存在该参数%s 重写该值为%s" % (setting, custom_settings[setting]))
                    continue
                options[setting.strip("-")] = custom_settings[setting]
        del warnings
        return PhantomJSOptions(service_args=["--{}={}".format(k, v) for k, v in options.items()],
                                dcap=dcap)

    raise AttributeError("其他浏览器驱动类型暂不支持")


class _WebDriver:

    def __init__(self, driver):
        self._driver = driver

    @property
    def driver(self):
        return self._driver

    def __enter__(self):
        return self._driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._driver:
            self._driver.quit()

    def quit(self):
        try:
            self._driver.quit()
        except Exception as e:
            traceback.print_exc()

    def close(self):
        try:
            self._driver.close()
        except Exception as e:
            traceback.print_exc()
