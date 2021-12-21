# -*- coding: utf-8 -*-
'''
    #!/usr/bin/env python
    # _*_ coding: utf-8 _*_
    # @Time : 2021/10/21 16:27
    # @Author : zhitong.he
    # @Version：V 0.1
    # @File : uac_yatsen_authtoken.py
    # @desc :
'''
import sqlalchemy
import json
import requests
from common.security.rsa import RsaGenKey, RsaSecurity

def UacYatsenAuthtoken(username,password) -> str:
    url = "http://api.yatsenglobal.com/uac/oauth/token"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = 'client_id={}&client_secret={}&grant_type=client_credentials'.format(username,
                                                                                   password)
    response = requests.request("POST", url, headers=headers, data=payload)
    datajson = json.loads(response.text)
    return datajson['access_token']

def UacYatsenIdFromDB(cookie_code:str, dsn:str, private_pem:str):
    sql = "SELECT id, platform, cookie_code, account_name , login_uname, login_pwd from platform_accounts WHERE cookie_code = '{cookie_code}'"
    engine = sqlalchemy.create_engine(dsn)
    ret = engine.execute(sql.format(cookie_code=cookie_code)).fetchall()
    if not ret or len(ret) == 0:
        print("无此相应的cookie_code 账号信息")
        return
    rsa_cipher = RsaSecurity.new(private=private_pem)
    login_uname = rsa_cipher.decrypt(ret[0].login_uname)
    login_pwd = rsa_cipher.decrypt(ret[0].login_pwd)
    return login_uname,login_pwd

queryUserNameByCookieCode = UacYatsenIdFromDB

def UacYatsenAuthtokenWithId(cookie_code,dsn,private_pem) -> str:

    username, password = UacYatsenIdFromDB(cookie_code=cookie_code,dsn=dsn,private_pem=private_pem)
    # print(username,password)
    access_token = UacYatsenAuthtoken(username=username, password=password)
    # print(access_token)
    return access_token



