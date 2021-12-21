# -*- coding: utf-8 -*-
"""
common cookies - 通用的cookies处理模块
"""


def list2dict(cookies_list):
    """
    cookies list转dict
    :param cookies_list: list of dict, [{'name': ..., 'value': ...}]
    :return: dict, like: {key1: value1, key2: value2, ...}
    """
    cookies_dict = dict()
    for ehe in cookies_list:
        cookies_dict[ehe['name']] = ehe['value']
    return cookies_dict


def list2str(cookies_list, sep='; ', equ='='):
    """
    cookie list转str
    :param cookies_list: list of dict, [{'name': ..., 'value': ...}]
    :param sep: str,
    :param equ: str,
    :return: str, like: 'key1=value1; key2=value2'
    """
    cookies_str = [x['name'] + equ + x['value'] for x in cookies_list]
    cookies_str = sep.join(cookies_str)
    return cookies_str


def str2dict(cookies_str, sep='; ', equ='='):
    """
    cookies str转dict
    :param cookies_str: str,
    :param sep: str,
    :param equ: str,
    :return: dict, like: {key1: value1, key2: value2, ...}
    """
    cookies_dict = dict()
    list_tmp = cookies_str.split(sep)
    for ehe in list_tmp:
        tmp = ehe.split(equ)
        if len(tmp) > 1:
            cookies_dict[tmp[0]] = equ.join(tmp[1:])
    return cookies_dict


def dict2str(cookies_dict, sep='; ', equ='='):
    """
    cookies dict转str
    :param cookies_dict: dict,
    :param sep: str,
    :param equ: str,
    :return: str, like: 'key1=value1; key2=value2'
    """
    cookies_str = [ehkey + equ + cookies_dict[ehkey] for ehkey in cookies_dict.keys()]
    cookies_str = sep.join(cookies_str)
    return cookies_str
