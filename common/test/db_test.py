# -*- coding: utf-8 -*-

import logging
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, VARCHAR, DATETIME, TEXT, Integer
from common import dbmodule

__base = declarative_base()


class CookiesTable(__base):
    __tablename__ = 'cookies'

    cookiesid = Column(VARCHAR(100), primary_key=True)
    cookies = Column(TEXT, nullable=False)
    inserttime = Column(DATETIME)
    id = Column(Integer, primary_key=True)


if __name__ == '__main__':
    dsn = 'mysql+pymysql://msl:153339@localhost:3306/kol_spider?charset=utf8mb4'
    conn = create_engine(dsn)
    sessmaker = sessionmaker(conn)
    sess = sessmaker()

    data = {
        'cookiesid': '001',
        'cookies': 'cookiestest',
        'inserttime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'id': 100
    }
    # dbmodule.orm_update_or_insert(sess, data, ['cookiesid'], CookiesTable, update=False)
    # dbmodule.orm_update_or_insert(sess, data, ['cookies', 'num'], CookiesTable, update=True, updatekeys=['inserttime'])
    dbmodule.update_or_insert(sess, data, ['cookies'], 'cookies', update=True, updatekeys=['inserttime', 'id'])
    sessmaker.close_all()
