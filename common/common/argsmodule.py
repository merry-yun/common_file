# -*- coding: utf-8 -*-

import argparse



def get_args(addargs_dict):
    """
    命令行启动时获取命令行参数
    :param addargs_dict: dict,
    :return: dict, 
    """
    parser = argparse.ArgumentParser()
    for ehkey in addargs_dict.keys():
        parser.add_argument(ehkey, **addargs_dict[ehkey])
    args = parser.parse_args()
    return args
