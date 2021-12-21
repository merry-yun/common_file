# -*- coding: utf-8 -*-

from common.tools import ListCookies
import pandas as pd

if __name__ == '__main__':
    a = ListCookies()
    b = a.get_cookies_all()
    df = pd.DataFrame(b)
    df = df[['cookiesid', 'inserttime', 'cookies']]
    df.sort_values(by='cookiesid', inplace=True)
    df.to_excel('./listtools_test.xlsx', index=False)
