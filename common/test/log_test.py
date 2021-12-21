# -*- coding: utf-8 -*-

import logging
from common import logmodule


if __name__ == '__main__':
    dirpath = 'E:/Python_re/common/test'
    filename = 'log_test.log'
    logmodule.save_log_setting(dirpath, filename)
    logging.info('info msg')
    logging.warning('warning msg')
    logging.error('error msg')
