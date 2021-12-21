#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2021-10-19 17:07
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2021-10-19 17:07
 * @Desc: common
'''
import json

import requests
from functools import partial
from scrapy.http.request import Request


def _sign_request(api_url: str, encrypt_url: str, encrypt_cookie: str, request_callback: object):
    encrypt_data = dict(url=encrypt_url, cookie=encrypt_cookie)
    # inline_callback =
    # partial_func = lambda response: _parse_sign(response=response, callback=inline_callback)
    parse_sign_callback = partial(_parse_sign, request_callback=request_callback)
    return Request(url=api_url,
                   body=json.dumps(encrypt_data).encode(),
                   callback=parse_sign_callback,
                   dont_filter=True,
                   meta=dict(dont_retry=True))


def _parse_sign(response, request_callback):
    sign = response.body.decode("utf8", "ignore").strip()
    return request_callback(sign=sign)


def TTEncryptSign(api_url: str, encrypt_url: str, encrypt_cookie: str, request_callback: object = None,
                  mode: str = 'twisted'):
    if mode == 'twisted':
        return _sign_request(api_url, encrypt_url, encrypt_cookie, request_callback)
    elif mode == 'sync':
        if request_callback is None:
            request_callback = lambda x: x
        return _sign_request_sync(api_url, encrypt_url, encrypt_cookie, request_callback)
    else:
        raise ValueError("缺少该方法的声明 %s" % mode)


def _sign_request_sync(api_url, encrypt_url, encrypt_cookie, request_callback):
    encrypt_data = dict(url=encrypt_url, cookies=encrypt_cookie)
    response = requests.post(url=api_url, json=encrypt_data)
    sign = response.content.decode("utf8", "ignore").strip()
    return request_callback(sign=sign)


"""
示范脚本
from common.tools.hashlibs.toutiao_sign import TTEncryptSign
from functools import partial


class DemoSpider(scrapy.Spider)
    ...

    def get_sign(self, url, cookies, meta):
        node_url = self.settings['TTENCRYPT_SIGN_API']
        # data = {
        #     "url": url,
        #     "cookies": cookies
        # }
        # response = requests.post(node_url, json=data)
        # sign = response.text
        request_callback = partial(self.test, url=url, meta=meta)
        ss = TTEncryptSign(node_url, url, cookies, request_callback)
        return ss

    def test(self, sign, url, meta):
        result_url = url + '&_signature=' + sign
        headers = meta['headers']
        return Request(result_url, headers=headers, meta=meta, cookies=self.cookies, dont_filter=True)
"""