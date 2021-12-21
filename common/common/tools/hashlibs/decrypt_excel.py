# -*- coding: utf-8 -*-
'''
    #!/usr/bin/env python
    # _*_ coding: utf-8 _*_
    # @Time : 2021/10/25 18:46
    # @Author : zhitong.he
    # @Version：V 0.1
    # @File : decrypt_excel.py
    # @desc :
'''
import msoffcrypto
import io


def DecryptExcel(fpath:str, password:str, fobj) -> bool:
    """
    fpath: 保存解密的路径
    password:  解密密码
    fobj: 这是一个文件句柄 open(fname, "wb")
    """
    try:
        with open(fpath, "wb") as newFobj:
            file = msoffcrypto.OfficeFile(fobj)
            file.load_key(password=password)  # Use password
            file.decrypt(newFobj)
        return True
    except Exception as e:
        print("save err reason: %s" % e)
        return False