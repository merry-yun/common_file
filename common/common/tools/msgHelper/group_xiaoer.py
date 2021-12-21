#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2021/1/5 17:29
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2021/1/5 17:29
 * @Desc: common

 群发送文件助手
'''
import json
import urllib.request
import logging
from urllib3 import encode_multipart_formdata

logger = logging.getLogger(__name__)


class GroupFileXiaoer:
    """
    群小二 发送文件
    """

    webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key="

    def __init__(self, fpath, group_uuid):
        """
        fp: *.read() like file-object
        group_uuid: a robot key
        """
        self.group_uuid = group_uuid
        self._fpath = fpath

    def _get_media_id(self):

        uploadfile_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={key}&type=file".format(
            key=self.group_uuid)
        filename = self._fpath.split("/")
        if len(filename) < 2:
            filename = self._fpath.split("\\")
        data = {
            "media": (
                filename[-1],
                open(self._fpath, mode='rb').read()
            )
        }
        encode_data, content_type = encode_multipart_formdata(data)

        req = urllib.request.Request(url=uploadfile_webhook,
                                     data=encode_data,
                                     headers={"content-type": content_type})
        resp = urllib.request.urlopen(req)
        res = json.loads(resp.read())
        if res["errmsg"] != "ok":
            return None, 500
        return res["media_id"], 200

    def send(self):

        media_id, status = self._get_media_id()
        if status != 200:
            logger.warning("文件上传异常  操作失败")
            return

        data = {
            "msgtype": "file",
            "file": {
                "media_id": media_id
            }
        }
        self._opener(data=data)

    def _opener(self, data):
        webhook = self.webhook + self.group_uuid
        try:
            req = urllib.request.Request(url=webhook,
                                         data=json.dumps(data).encode(),
                                         headers={"content-type": "application/json"})
            resp = urllib.request.urlopen(req)
            res = json.loads(resp.read())
            if res["errmsg"] == "ok":
                logger.info("文件发送成功")
                return
            logger.info("文件发送失败 %s" % res["errmsg"])
        except Exception as e:
            logger.info("文件发送失败 %s" % e)


class GroupImageXiaoer(GroupFileXiaoer):
    hash_md_encode = None
    base64_encode = None

    def __init__(self, fpath, group_uuid):
        super(GroupImageXiaoer, self).__init__(fpath, group_uuid)
        self._default_encode()

    def _default_encode(self):
        import hashlib
        import base64

        def _hash_md5_encode(x):
            m = hashlib.md5()
            m.update(x)
            return m.hexdigest()

        def _base64_encode(x):
            return base64.b64encode(x).decode()

        self.hash_md_encode = _hash_md5_encode
        self.base64_encode = _base64_encode

    def send(self):
        with open(self._fpath, mode="rb") as fp:
            fp_content = fp.read()

        m = self.hash_md_encode(fp_content)
        b = self.base64_encode(fp_content)
        data = {
            "msgtype": "image",
            "image": {
                "base64": b,
                "md5": m
            }
        }

        self._opener(data=data)


class GroupTextXiaoer(GroupFileXiaoer):

    def __init__(self, fpath, group_uuid):
        """
        fpath can be a file-object or dict or str
        if fpath is file-object
            The `data` variable will be initialized to
            {
                "msgtype": "text",
                "text": {
                    "content": self._fpath.read().decode(),
                }
            }
        if fpath is dict
            data = self._fpath

        if fpath is str
            {
                "msgtype": "text",
                "text": {
                    "content": self._fpath,
                }
            }
        """
        super(GroupTextXiaoer, self).__init__(fpath, group_uuid)

    def send(self):

        if isinstance(self._fpath, dict):
            data = self._fpath
        elif hasattr(self._fpath, "read") and not isinstance(self._fpath, str):
            data = {
                "msgtype": "text",
                "text": {
                    "content": self._fpath.read().decode(),
                }
            }
        elif isinstance(self._fpath, str):
            data = {
                "msgtype": "text",
                "text": {
                    "content": self._fpath,
                }
            }
        else:
            logger.warning("fpath变量类型应为 file-object/dict/str的其中一种, 而不是 `%s`" % type(self._fpath))
            return

        self._opener(data=data)

    @staticmethod
    def format_(msgtype, content, *mentioned_list):

        if msgtype not in ("text", "markdown"):
            logger.warning("msgtype only can be text/markdown, instead of %s" % msgtype)
            return

        if not isinstance(content, str):
            logger.warning("content only can be str, instead of %s" % type(content))
            return

        data = {
            "msgtype": msgtype,
            msgtype: {
                "content": content
            }
        }
        if len(mentioned_list) > 0:
            data["mentioned_list"] = list(mentioned_list)
        return data


class GroupNewsXiaoer(GroupFileXiaoer):

    def send(self):

        if isinstance(self._fpath, dict):
            data = self._fpath
        elif hasattr(self._fpath, "read") and not isinstance(self._fpath, str):
            data = json.loads(self._fpath.read())
        else:
            logger.warning("fpath变量类型应为 file-object/dict的其中一种, 而不是 `%s`" % type(self._fpath))
            return

        self._opener(data=data)

    @staticmethod
    def format_(title, url, picurl=None, description=None):

        if not isinstance(title, str) or not isinstance(url, str):
            logger.warning("title/url only can be str, instead of %s/%s" % (type(title), type(url)))
            return

        data = {
            "msgtype": "news",
            "news": {
                "articles": [
                    {
                        "title": title,
                        "description": description,
                        "url": url,
                        "picurl": picurl
                    }
                ]
            }
        }
        return data
