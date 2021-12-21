#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2020/9/22 16:24
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2020/9/22 16:24
 * @Desc: common
'''
import json
import logging
import os
import requests
import urllib.parse


class LocalStorageResponse:

    def __init__(self, content, url):
        self.content = content
        self.url = url

    def json(self):
        return json.loads(self.content)

    @property
    def text(self):
        return self.content.decode()

    @property
    def body(self):
        return self.content


class Session:

    def __init__(self, save_path: str):

        self.save_path = save_path
        self.sess = requests.Session()
        self.body = None

    def post(self, *args, **kwargs):

        self.body = self.sess.post(*args, **kwargs)
        return self.body

    def get(self, *args, **kwargs):

        self.body = self.sess.get(*args, **kwargs)

        return self.body

    def save_localstorage(self, fname=None):

        url = self.body.url
        pp = urllib.parse.urlparse(url)
        dirpath = os.path.abspath(os.path.join(self.save_path, "./" + pp.netloc))

        if not os.path.exists(dirpath):
            os.mkdir(dirpath)

        files = pp.path.split("/")
        for doc in files[:-1]:
            dirpath = dirpath + "/" + doc

            if not os.path.exists(dirpath):
                os.mkdir(dirpath)
        else:
            if fname is not None:
                fname = fname
            elif files[-1].find("?") > 0:
                fname = files[-1].split("?")[0]
            else:
                fname = files[-1]
            logging.info("downloading url `%s` in localstorage path `%s`" % (self.body.url, dirpath))
            try:
                with open(dirpath + "/" + fname, "wb") as fp:
                    fp.write(self.body.content)
                logging.info("save `%s`...ok" % self.body.url)
            except Exception as e:
                logging.warning("save `%s`...fail by {%s}" % (self.body.url, e))

    def test_request(self, method: str, url: str, **kwargs):

        _u = urllib.parse.urlparse(url)
        filepath = os.path.abspath(os.path.join(self.save_path, "./" + _u.netloc + "/" + _u.path))
        logging.info("[%s] `%s` replace into localstorage path `%s`" % (method, url, filepath))
        with open(file=filepath, errors="ignore", encoding="utf8") as fp:
            content = fp.read()
        return LocalStorageResponse(content, url)
