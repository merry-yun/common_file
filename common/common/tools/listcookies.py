# -*- coding: utf-8 -*-


"""
本地redis的cookies全读取
"""

import redis


class ListCookies(object):
    """
    本地redis的cookies全读取
    """
    def __init__(self):
        self.rdb = redis.Redis(socket_keepalive=True)

    def read_keys_all(self):
        return self.rdb.keys()

    def read_cookies2hash(self, hname, kname):
        """
        从redis数据库-hash内获取cookies
        :param hname: str, hash名称
        :param kname: str, hash内的键名
        :return: None/str, hash内的键名对应值
        """
        kvalue = self.rdb.hget(hname, kname)
        if kvalue is not None:
            kvalue = kvalue.decode('utf-8')
        return kvalue

    def get_cookies_all(self):
        """
        从redis数据库内获取所有cookies
        :return: list of dict,
        """
        keys = self.read_keys_all()
        item_list = list()
        for ehkey in keys:
            res_tmp = self.rdb.hgetall(ehkey)
            res_tmp['cookiesid'] = ehkey
            res = dict()
            for ehkey in res_tmp:
                if type(ehkey) is bytes:
                    if type(res_tmp[ehkey]) is bytes:
                        res[ehkey.decode()] = res_tmp[ehkey].decode()
                    else:
                        res[ehkey.decode()] = res_tmp[ehkey]
                else:
                    if type(res_tmp[ehkey]) is bytes:
                        res[ehkey] = res_tmp[ehkey].decode()
                    else:
                        res[ehkey] = res_tmp[ehkey]
            item_list.append(res)
        # print(item_list)
        return item_list

    def close(self):
        self.rdb.close()
