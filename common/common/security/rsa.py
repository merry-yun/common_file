#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2021/2/18 18:07
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2021/2/18 18:07
 * @Desc: common
'''
from common.security import BaseSecurity
from zope.interface.declarations import implementer
from base64 import b64encode, b64decode


class RsaGenKey:

    def __init__(self, rsa):
        self.rsa = rsa

    @classmethod
    def new(cls):
        from Crypto import Random
        from Crypto.PublicKey import RSA

        r_gen = Random.new().read
        rsa = RSA.generate(1024, r_gen)
        return cls(rsa)

    def exportPublicKey(self, fname=None):
        if fname is None:
            fname = "public.pem"

        pk = self.rsa.publickey().exportKey()
        # print(pk)
        with open(fname, "wb") as fp:
            fp.write(pk)

    def exportPrivateKey(self, fname=None):

        if fname is None:
            fname = "private.pem"

        pk = self.rsa.exportKey()
        # print(pk)
        with open(fname, "wb") as fp:
            fp.write(pk)


@implementer(BaseSecurity)
class RsaSecurity:
    v = "V21"
    random: object

    def __init__(self, public, private):
        self.public = public
        self.private = private

    def encrypt(self, s):
        if not isinstance(s, bytes):
            s = s.encode()
        b = self.public.encrypt(s)
        sign = "%d%s" % (0, self.v)
        return self.v + b64encode(b).decode() + "." + b64encode(sign.encode()).decode()

    def decrypt(self, s):
        if s.startswith(self.v):
            s = s[3:]
        s = b64decode(s.split(".")[0])
        b = self.private.decrypt(s, self.random.new(1024).read)
        return b.decode()

    @classmethod
    def new(cls, **kwargs):

        from Crypto.Cipher import PKCS1_v1_5
        from Crypto import Random
        from Crypto.PublicKey import RSA

        if "public" in kwargs:
            with open(kwargs['public'], 'rb') as fp:
                p = fp.read()
            cpublic = PKCS1_v1_5.new(RSA.importKey(p))
        else:
            cpublic = None

        if "private" in kwargs:
            with open(kwargs["private"], "rb") as fp:
                p = fp.read()
            cprivate = PKCS1_v1_5.new(RSA.importKey(p))
            cls.random = Random
        else:
            cprivate = None

        return cls(private=cprivate, public=cpublic)
