# common
通用模块 安装方式参考下列命令行
```
安装方式 git clone git@gitlab.corp.yatsenglobal.com:spider/common.git
python setup.py install
简单的功能 反射数据库的表结构生成scrapy的item类
common genitem --table 表名(必须) --scheme 数据库名(非必须)
```

# 说明文档
更多模块说明 [见链接](doc/doc.md)

## 模块介绍
名称 | 用途
:-- | :--
emailmodule | 邮件发送模块
logmodule | 日志模块
cookiesmodule | cookies模块
argsmodule | 命令行参数读取模块
dbmodule | 数据库插入/更新模块(ORM)
tools/listcookies | 本地redis的cookies全读取
tools/msgHelper/send | 企业微信-数据分析组发送模块 
json2sql | json对象转化为sql建表对象


## json2sql 使用方式

```
from common.json2sql import serialize

jq = serialize.Json2SQL()
suffix = "`thedate` date DEFAULT NULL COMMENT '日期',\n" \
      "`updatetime` datetime(0) NULL DEFAULT NULL COMMENT '更新時間',\n" \
      "`inserttime` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '插入時間',\n" \
      "`cookiesid` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '帐号',\n"
pks = ("cookiesid", "thedate")
tbn_path = "/home/module/test"
# 传入参数
jq.decode(body=json.load(open("test.json", encoding="utf8", errors="ignore")),
          suffix=suffix,
          tbn="test",
          with_prefix=False)

#将在/home/module目录下生成test_structure.sql文件
jq.to_file(tbn=tbn_path)

```

# 日志更新列表
## 更新common.scrapy模块
该模块是将常用scrapy组件进行公用化
```angular2
// 例如 pipline 组件
// 在settings.py/custom_settings配置如下
// 这两个pipeline读取DSN参数进行数据库连接 增加了命令行SELECTED_DSN作为数据库配置参数
// e.g scrapy crawl your_spider -s SELECTED_DSN=YOUR_CONFIG_DSN # 届时就会读取你settngs.py的YOUR_CONFIG_DSN变量，详情阅读源码


ITEM_PIPELINES = {
    # 只增不更新 要求settings.py必须要有DSN变量作为数据库链接和spider类的sql属性 
   'common.scrapy.pipelines.MySQLInsertPipeline': 300, 
   # 检查更新 要求settings.py必须要有DSN变量作为数据库链接和spider类的sql属性,primary_keys属性以及 sql_mode属性(update/insert_or_update)
   'common.scrapy.pipelines.MySQLUpdateOrInsertPipeline': 302, 
   # 多个item检查更新 要求item类的sql属性,primary_keys属性以及 sql_mode属性(insert/insert_or_update)
   'common.scrapy.pipelines.MulitItemsPipeline': 302, 

}

// 该下载中间件负责代理轮询，添加，重试。参数如下
DOWNLOADER_MIDDLEWARES = {
    "common.scrapy.middlewares.proxy_pool.ProxyPoolDownloadMiddleWare":200
}
PROXY_REDIS_URL = "redis://*****"
DOWNLOAD_TIMEOUT = 3


// 下列是上传日志到指定数据库表格中，方便以后统计监测
// 使用操作
// 1. 更新common最新主支代码，添加到PYPATH
// 2. 在每个项目settings.py文件中添加下列代码即可使用
EXTENSIONS_BASE = {
    # 'scrapy.extensions.telnet.TelnetConsole': None,
    # 将自定扩展添加全局初始化extensions
    'common.scrapy.extensions.logStatExtension.LogStatUpdateExtension': 999,
    # scrapy本身默认扩展
    # 'scrapy.extensions.memusage.MemoryUsage': 0,
    # 'scrapy.extensions.memdebug.MemoryDebugger': 0,
    # 'scrapy.extensions.closespider.CloseSpider': 0,
    # 'scrapy.extensions.feedexport.FeedExporter': 0,
    # 'scrapy.extensions.spiderstate.SpiderState': 0,
    # 'scrapy.extensions.throttle.AutoThrottle': 0,
    'scrapy.extensions.corestats.CoreStats': 0,
    'scrapy.extensions.telnet.TelnetConsole': 0,
    'scrapy.extensions.logstats.LogStats': 0,
}
LOG_WATCHER = 'mysql+pymysql://root:123456@localhost:3306/spider_taowai?charset=utf8mb4'
```

## 增加selenium下载中间件
```
# 示例模板代码 更多参数使用设置看源码
# -*- coding: utf-8 -*-
import logging

import scrapy
"""
Hello, ali_selenium
DataDir:
请填写该爬虫的数据路径
"""
from common.scrapy.spiders.request import RenderRequest


class AliSeleniumSpider(scrapy.Spider):
    name = 'ali_selenium'
    allowed_domains = ['baidu.com']
    start_urls = ['http://baidu.com/']

    custom_settings = {
        "SELENIUM_HEADLESS": True,
        "SELELNIUM_DRIVER": "phantomjs",
        "SELENIUM_EXECUTABLE_PATH": r"G:\tmp\phantomjs-2.1.1-windows\phantomjs-2.1.1-windows\bin\phantomjs.exe",
        "DOWNLOADER_MIDDLEWARES": {
            "common.scrapy.middlewares.selenium_downloadmiddleware.SeleniumDownloadMiddleware": 1
        },
        "SELENIUM_KWARGS":{}
    }

    def __init__(self, *args, **kwargs):
        scrapy.Spider.__init__(self, *args, **kwargs)
        if "tbn" in kwargs:
            self.tbn = kwargs['tbn']
            self.logger.info("save tbn is " + self.tbn)

        logger = logging.getLogger("selenium.webdriver.remote.remote_connection")
        logger.setLevel(logging.ERROR)
        logger = logging.getLogger("urllib3.connectionpool")
        logger.setLevel(logging.ERROR)

    def start_requests(self):
        """
        请创建你的初始请求任务
        """
        yield RenderRequest(
            url="https://login.taobao.com/",
            driver_callback=self.driver_parse,
            script_js="return window._n",
            callback=self.parse
        )

    def parse(self, response):
        """
        请开始编写你的解析器
        与之前scrapy的解析模板
        """
        print(response.body[:100])
        print(response.url)
        print(response.meta["js_result"])

    def driver_parse(self, driver, request):
        """
        这里是浏览器驱动操作回调函数
        输入变量固定是driver, request
        返回值 void/Request/Response 三选一
        :param driver:
        :param request:
        :return:
        """
        pass

```


## 更新common.selelogin模块
创建BaseLoginMixin和BaseLoginAbstract基类，通过继续实现相应渠道的登录操作。

增加webdriver_pool 以及webdriver 类 支持过期回收浏览器实例, 多开浏览器实现webdriver pool , 以及远程调用渲染集群(需要通过自己socket通信协议)

## 更新common.tools.msgHelper模块
新增群发送Xiaoer以及文件导出Xiaoer
```js
'''
群发送助手
'''
from common.tools.msgHelper import group_xiaoer
fp = open("xxx", encoding="utf8")
group_uuid = "xxxx-xxx-xx-xx-x-x"
# 文件发送
xiaoer = group_xiaoer.GroupFileXiaoer(fp, group_uuid)
xiaoer.send()

# 图片发送
xiaoer = group_xiaoer.GroupImageXiaoer(fp, group_uuid)
xiaoer.send()

# 文本消息发送
## 如果需要定制消息格式 可以使用format_静态方法
data = group_xiaoer.GroupTextXiaoer.format_(msgtype, content, *mentioned_list)
xiaoer = group_xiaoer.GroupTextXiaoer(data, group_uuid)
xiaoer.send()

# 图文消息发送
## 如果需要定制消息格式 可以使用format_静态方法
data = group_xiaoer.GroupNewsXiaoer.format_(title, url, picurl, description)
xiaoer = group_xiaoer.GroupNewsXiaoer(data, group_uuid)
xiaoer.send()
```

-----------------
```js
'''
文件导出助手
'''

from common.tools.msgHelper import file_xiaoer
xiaoer = file_xiaoer.FileXiaoer(
    conn=sqlalchemy.create_engine(dsn),
    filename=filename
)
xiaoer.execute(sql)
xiaoer.to_file()
xiaoer.get_abs_path()

## 如果有需要使用多个sheet合并excel 可使用to_excel_sheets方法
xiaoer = file_xiaoer.FileXiaoer(
    conn=sqlalchemy.create_engine(dsn),
    filename=filename
)
xiaoer.to_excel_sheets(
    {
    "sheet1": sql1,
    "sheet2": sql2    
}
)
xiaoer.get_abs_path()
```

##　新增tools.boxs 工具箱模板
```js
时间工具箱 from tools.boxs.time_box import *

```
## 更新tools.test_requests.requests模块
该模块是将网页内容暂存在本地文件目录上，通过test_request方法获取到本地内容。

```angular2
// 用途: 避免过多重放攻击导致次数受限制
import logging
logging.basicConfig(level=logging.INFO)
from common.tools.requests_test.requests import Session

s = Session(save_path=r"G:\tmp\新建文件夹")
s.post(url="https://g.alicdn.com/alilog/mlog/aplus_v2.js")
s.save_localstorage()
s.test_request(method='GET', url="https://g.alicdn.com/alilog/mlog/aplus_v2.js")

```
