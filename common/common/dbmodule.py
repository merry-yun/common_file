# -*- coding: utf-8 -*-

# import logging
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base

import hashlib

def orm_update_or_insert(session, data, filtkeys, table, update=False, updatekeys=None):
    """
    基于orm更新/插入数据
    :param session: sessionmaker(),
    :param data: dict/series,
    :param filtkeys: list, 键名, 用于筛选数据
    :param table:
    :param update: bool, 是否update数据
    :param updatekeys: list, 键名, 用于update数据
    """
    filt_dict = dict()
    for ehfkey in filtkeys:
        filt_dict[ehfkey] = data[ehfkey]
    res_filted = session.query(table).filter_by(**filt_dict).all()
    # print(len(res_filted))
    # update
    if len(res_filted) > 0:
        if (update is True) and isinstance(updatekeys, list):
            for ehrf in res_filted:
                for ehukey in updatekeys:
                    # print(ehukey, data[ehukey])
                    if hasattr(ehrf, ehukey):
                        setattr(ehrf, ehukey, data[ehukey])
                session.commit()
    # insert
    elif len(res_filted) <= 0:
        data_insert = table(**data)
        session.add(data_insert)
        session.commit()


def update_or_insert(session, data, filtkeys, tbn, update=False, updatekeys=None):
    """
    基于sql语句更新/插入数据
    :param session: sessionmaker(),
    :param data: dict/series,
    :param filtkeys: list, 键名, 用于筛选数据
    :param tbn: str, table name
    :param update: bool, 是否update数据
    :param updatekeys: list, 键名, 用于update数据
    """
    filt_dict = dict()
    for ehfkey in filtkeys:
        filt_dict[ehfkey] = data[ehfkey]
    filt_str = ['`%s`="%s"' % (x, filt_dict[x]) for x in filt_dict.keys()]
    filt_str = ' AND '.join(filt_str)
    sql = 'SELECT * FROM `%s` WHERE %s' % (tbn, filt_str)
#    print(sql)
    res = session.execute(sql)
    if res.rowcount > 0:
        if update is True:
            update_str = ['`%s`="%s"' % (x, data[x]) for x in updatekeys]
            update_str = ', '.join(update_str)
            sql = 'UPDATE `%s` SET %s WHERE %s' % (tbn, update_str, filt_str)
        else:
            return None
    else:
        sql = 'INSERT INTO `%s` (`%s`) VALUES (%s)' % \
              (tbn, '`, `'.join(list(data.keys())), ', '.join(['"%s"' % data[x] for x in data.keys()]))
 #   print(sql)
    session.execute(sql)
    session.commit()


def replace_c(session, data, filtkeys, tbn, update=False, updatekeys=None):
    """
    改版 update_or_insert 省去 第一步查询
    基于sql语句更新/插入数据
    :param session: sessionmaker(),
    :param data: dict/series,
    :param filtkeys: list, 键名, 用于筛选数据
    :param tbn: str, table name
    :param update: bool, 是否update数据
    :param updatekeys: list, 键名, 用于update数据
    """
    sql = 'REPLACE INTO `%s` (`%s`) VALUES (%s)' % \
          (tbn, '`, `'.join(list(data.keys())), ', '.join(['"%s"' % data[x] for x in data.keys()]))
    # if update is True:
    #     filt_dict = dict()
    #     for ehfkey in filtkeys:
    #         filt_dict[ehfkey] = data[ehfkey]
    #     filt_str = ['`%s`="%s"' % (x, filt_dict[x]) for x in filt_dict.keys()]
    #     filt_str = ' AND '.join(filt_str)
    #     update_str = ['`%s`="%s"' % (x, data[x]) for x in updatekeys]
    #     update_str = ', '.join(update_str)
    #     sql = 'UPDATE `%s` SET %s WHERE %s' % (tbn, update_str, filt_str)
    # else :
    #     sql = 'REPLACE INTO `%s` (`%s`) VALUES (%s)' % \
    #           (tbn, '`, `'.join(list(data.keys())), ', '.join(['"%s"' % data[x] for x in data.keys()]))
    #print(sql)
    session.execute(sql)
    session.commit()


def json2sql_query(json_s,tbn,miss_sets=set()):
    """
    一维一行json内容　转成　sql query　语句
    仅做字段变量创建快捷，注释和细节修改还是要靠自己
    仅包括：
        表结构字段构建
        insert value
    :param json_s: json
    :param tbn: 表名
    :return:　打印　sql query
    """

    sql = '`{field}` {type} DEFAULT NULL,'

    sql_query_str = f"DROP TABLE IF EXISTS {tbn};\nCREATE TABLE {tbn} ("

    tmp_set = set(['thedate', 'updatetime', 'inserttime', 'cookiesid'])
    want_set = set(json_s.keys()) - tmp_set - miss_sets
    item_dict = dict()
    print(want_set)
    for k in want_set:
        _k = k.lower()
        item_dict[_k] = json_s[k]
        if "date" in _k or "time" in _k:
            _type = "TIMESTAMP"
        elif _k.endswith("id"):
            _type = 'int(11)'
        elif isinstance(json_s[k], int):
            _type = 'int(11)'
        elif isinstance(json_s[k], float):
            _type = 'decimal(14, 4)'
        elif isinstance(json_s[k], bool):
            _type = 'tinyint(1)'
        elif isinstance(json_s[k], str):
            if len(json_s[k]) < 10:
                _len = 20
            elif 10 < len(json_s[k]) < 100:
                _len = 100
            else:
                _len = 255
            _type = 'varchar(%d)' % _len
        else:
            _type = "varchar(255)"
        sql_query_str = f'{sql_query_str} \n{sql.format(field=_k, type=_type)}'

    tmp = "`thedate` date DEFAULT NULL COMMENT '日期',\n" \
          "`updatetime` datetime(0) NULL DEFAULT NULL COMMENT '更新時間',\n" \
          "`inserttime` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '插入時間',\n" \
          "`cookiesid` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '帐号',\n" \
          "PRIMARY KEY (`thedate`, `cookiesid`) USING BTREE" \
          ") ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Compact;"

    sql_query_str = f'{sql_query_str} \n{tmp}'

    sql = 'INSERT INTO `%s` (`%s`) VALUES (%s)' % \
        (tbn, '`, `'.join(list(item_dict.keys())), ', '.join(['"%s"' % item_dict[x] for x in item_dict.keys()]))
    sql_query_str = f"{sql_query_str} \n {sql}"
    print(sql_query_str)


def md5(rb_string):
    # 对要加密的字符串进行指定编码
    rb_string = rb_string.encode(encoding='UTF-8')
    # 将md5 加密结果转字符串显示
    return hashlib.md5(rb_string).hexdigest()


def checkout_data(tbn, filt_dict):
    """
    检查数据
    :param tbn: 表名
    :param filt_dict: 筛选的条件，字典类型
    :return:
    """
    # 检查数据
    filt_str = ['`%s`="%s"' % (x, filt_dict[x]) for x in filt_dict.keys()]
    filt_str = ' AND '.join(filt_str)
    sql = 'SELECT * FROM `%s` WHERE %s' % (tbn, filt_str)
    print(sql)
    return sql
