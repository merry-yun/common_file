#!/usr/bin/env python 
# -*- coding:utf-8 -*- 
'''

 * @version: 0.0.0
 * @Company: 
 * @Author: zhanming.zhang 
 * @Date: 2020/6/24 17:23
 * @Last Modified by:   zhanming.zhang 
 * @Last Modified time: 2020/6/24 17:23
 * @Desc: common - 创建sql
'''


CREATE_DATABASE    = "DROP DATABASE IF EXISTS `%s`;\nCREATE DATABASE `%s` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;\n"
ADD_PRIVILEGES     = "GRANT ALL PRIVILEGES ON %v.* TO '%v'@'localhost';\nFLUSH PRIVILEGES;\n"
USE_DB             = "USE `%v`;\n"
CREATE_TABLE_BEGIN = "CREATE TABLE IF NOT EXISTS `%s` (\n"
CREATE_TABLE_END   = "\tPRIMARY KEY (%s) USING BTREE\n) ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT='%s';"
FIELD              = "\t`%s` %s  COMMENT '%s',\n"
FIELD_FOR_UPDATE   = "`%s` %s%s %s %s %s %s COMMENT '%s';\n"
DEFAULT_SUFFIX_SQL = "`thedate` date DEFAULT NULL COMMENT '日期',\n" \
                      "`updatetime` datetime(0) NULL DEFAULT NULL COMMENT '更新時間',\n" \
                      "`inserttime` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '插入時間',\n" \
                      "`cookiesid` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '帐号',\n"


def generateCreateSQL(node):

    _comment = ''
    if node.field.find("time") > 0:
        _type = "TIMESTAMP"
    elif node.type == int:
        if node.value > 2**31-1:
            _type = "bigint(20) DEFAULT NULL"
        else:
            _type = "int(11) DEFAULT NULL"
    elif node.type == bool:
        _type = "tinyint(2) DEFAULT NULL"
    elif node.type == float:
        _type = 'decimal(14, 4) DEFAULT NULL'
    elif node.type == str:
        if len(node.value) < 10:
            _len = 20
        elif 10 < len(node.value) < 100:
            _len = 100
        else:
            _len = 255
        _type = 'varchar(%d) DEFAULT NULL' % _len
    else:
        _type = 'varchar(255) DEFAULT NULL'

    return FIELD % (node.field, _type, _comment)