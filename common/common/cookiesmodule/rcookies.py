# -*- coding: utf-8 -*-
"""
redis cookies - redis的cookies存储/读取处理
"""

import datetime
import socket

import redis
import os
import base64


class RedisCookies(object):
    """
    本地redis的cookies存储/读取处理
    """
    ENCRYPT_KEY = True
    NOT_ALLOW_ENCRYPT_PREFIX = []
    ALLOW_ENCRYPT_PREFIX = ["ali", "jd", "pdd", "wph"]

    def __init__(self):
        if os.getenv("REDISHOST"):
            redis_url = os.getenv("REDISHOST")
            self.rdb = redis.Redis.from_url(url=redis_url)
        else:
            self.rdb = redis.Redis(host="10.2.0.98",
                                   password=base64.b64decode("WWF0U2VuMTIzNDU2").decode())
        if os.getenv("RSAPATH"):
            from common.security.rsa import RsaSecurity
            private = os.path.abspath(os.path.join(os.getenv("RSAPATH"), "./cookies_private.pem"))
            public = os.path.os.path.abspath(os.path.join(os.getenv("RSAPATH"), "./cookies_public.pem"))
            if os.path.exists(public) and os.path.exists(private):
                self.rsa_cipher = RsaSecurity.new(
                    private=private,
                    public=public
                )
            else:
                self.rsa_cipher = None
        else:
            self.rsa_cipher = None

    def save_cookies2hash(self, hname, kname, kvalue):
        """
        保存cookies到redis数据库-hash内
        :param kname: str, hash内的键名
        :param kvalue: str, hash内的键名对应值
        :param hname: str, hash名称
        :return:
            1 - 操作成功
            0 - 操作失败
        """
        kvalue = self._encrypt_cookie(hname=hname, kvalue=kvalue)
        return self.rdb.hset(hname, kname, kvalue)

    def read_cookies2hash(self, hname, kname):
        """
        从redis数据库-hash内获取cookies
        :param hname: str, hash名称
        :param kname: str, hash内的键名
        :return: None/str, hash内的键名对应值
        """
        kvalue = self.rdb.hget(hname, kname)

        print(f'hname :{hname}, kname :{kname}, kvalue:******')
        kvalue = self._decrypt_cookie(kvalue=kvalue)
        return kvalue

    def save_cookies2hash_withtime(self, hname, kvalue):
        """
        保存cookies到redis数据库-hash内, 包括插入时间和cookies值
        数据结构为: hname: {insertime: value, cookies: value， machine： 登录机器host}
        :param hname: str, hash名称
        :param kvalue: str, hash内的键名对应值
        :return:
            1 - 操作成功
            0 - 操作失败
        """
        today = datetime.datetime.today()
        today_str = today.strftime('%Y-%m-%d %H:%M:%S')
        self.rdb.hset(hname, 'inserttime', today_str)
        self.rdb.hdel(hname, 'machaine')
        self.rdb.hset(hname, 'machine', socket.gethostname())
        kvalue = self._encrypt_cookie(hname=hname, kvalue=kvalue)
        return self.rdb.hset(hname, 'cookies', kvalue)

    def read_cookies2hash_withtime(self, hname):
        """
        从redis数据库-hash内获取cookies, 不包括插入时间
        数据结构为: hname: {insertime: value, cookies: value}
        :param hname: str, hash名称
        :return: None/str, hash内的键名对应值
        """
        kvalue = self.rdb.hget(hname, 'cookies')
        if kvalue is not None:
            kvalue = kvalue.decode('utf-8')
        kvalue = self._decrypt_cookie(kvalue=kvalue)
        return kvalue

    def save_cookies(self, kname, kvalue, ex=None):
        """
        直接保存cookies到redis数据库内
        :param kname: str, 键名
        :param kvalue: str, 键名对应值
        :param ex: int, 过期时间(s), 默认None, 不过期
        :return:
            1 - 操作成功
            0 - 操作失败
        """
        kvalue = self._encrypt_cookie(hname=kname, kvalue=kvalue)
        return self.rdb.set(kname, kvalue, ex=ex)

    def read_cookies(self, kname):
        """
        从redis数据库内获取cookies
        :param kname: str, 键名
        :return: None/str, 键名对应值
        """
        kvalue = self.rdb.get(kname)
        if kvalue is not None:
            kvalue = kvalue.decode('utf-8')
        kvalue = self._decrypt_cookie(kvalue=kvalue)
        return kvalue

    def close(self):
        self.rdb.close()

    def _encrypt_cookie(self, hname, kvalue: str) -> str:
        if self.ENCRYPT_KEY and \
                (not any((hname.startswith(x) for x in self.NOT_ALLOW_ENCRYPT_PREFIX)) or
                 any((hname.startswith(x)) for x in self.ALLOW_ENCRYPT_PREFIX)) and \
                self.rsa_cipher:
            kvalue = self.rsa_cipher.encrypt(kvalue)
        return kvalue

    def _decrypt_cookie(self, kvalue: str) -> str:
        if isinstance(kvalue, bytes):
            kvalue = kvalue.decode()
        if kvalue is not None and kvalue.startswith("V21"):
            kvalue = self.rsa_cipher.decrypt(kvalue)
        return kvalue
