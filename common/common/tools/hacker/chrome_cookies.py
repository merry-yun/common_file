#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: samuel.zhang
 * @Date: 2020/9/23 11:19
 * @Last Modified by:   samuel.zhang
 * @Last Modified time: 2020/9/23 11:19
 * @Desc: common
获取本地浏览器的cookie记录并解密
'''
import base64
import json
import sqlite3

import jsonpath

import win32crypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# Contains base64 random key encrypted with DPAPI.
kOsCryptEncryptedKeyPrefName = "os_crypt.encrypted_key"

# AEAD key length in bytes.
kKeyLength = 256 // 8

# AEAD nonce length in bytes.
kNonceLength = 96 // 8

# Version prefix for data encrypted with profile bound key.
kEncryptionVersionPrefix = "v10".encode()

# Key prefix for a key encrypted with DPAPI.
kDPAPIKeyPrefix = "DPAPI"


LoginStateDir = "Login State 文件位置"
CookiesDB = "Cookies 位置"

class Aead:
    key_bytes = None

    def init(self, key: bytes):
        self.key_bytes = key

    def Open(self, raw_ciphertext: bytes, nonce: bytes, associate_str: bytes, plaintext: bytes):

        nonce_bytes = nonce
        ad_bytes = associate_str
        # data = base64.b64decode(ciphertext)
        data = raw_ciphertext

        aesgcm = AESGCM(self.key_bytes)
        return aesgcm.decrypt(nonce_bytes, data, ad_bytes)


def GetEncryptionKeyInternal():

    content = json.load(open(LoginStateDir))
    return jsonpath.jsonpath(content, kOsCryptEncryptedKeyPrefName)[0]


def DecryptStringWithDPAPI(ciphertext, plaintext):
    return win32crypt.CryptUnprotectData(ciphertext, None, None, None, 0)


def OSCryptDecryptString(ciphertext, plaintext):
    if not ciphertext.startswith(kEncryptionVersionPrefix):
        return DecryptStringWithDPAPI(ciphertext, plaintext)

    aead = Aead()
    key = GetEncryptionKeyInternal()
    encryptedKeyBytes = base64.b64decode(key)[5:]
    _, keyBytes = DecryptStringWithDPAPI(ciphertext=encryptedKeyBytes, plaintext=None)
    aead.init(keyBytes)

    # Obtain the nonce.
    nonce = ciphertext[len(kEncryptionVersionPrefix):len(kEncryptionVersionPrefix) + kNonceLength]

    # Strip off the versioning prefix before decrypting.
    raw_ciphertext = ciphertext[len(kEncryptionVersionPrefix) + kNonceLength:]

    return ('', aead.Open(raw_ciphertext,
                     nonce,
                     b"",
                     plaintext))


"""
# demo
def test_unit_os_crypt_win():

    # 获取Cookies DB位置
    conn = sqlite3.connect(CookiesDB)
    cursor = conn.cursor()
    cursor.execute("SELECT host_key, encrypted_value FROM cookies LIMIT 10")
    result = cursor.fetchall()
    cursor.close()

    # 对Cookies进行解析
    for host_key, encryted_value in result:
        print(host_key, OSCryptDecryptString(ciphertext=encryted_value, plaintext=b''))
"""