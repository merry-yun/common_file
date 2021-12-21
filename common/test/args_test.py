# -*- coding: utf-8 -*-

from common import argsmodule


if __name__ == '__main__':
    addargs_dict = {
        '-u': {'help': 'username', 'type': str, 'default': 'username'},
        '-p': {'help': 'password', 'type': str, 'default': 'password'},
        '-id': {'help': 'cookies id', 'type': str, 'default': 'cookies id 1'},
    }
    args = argsmodule.get_args(addargs_dict)
    print(args)
