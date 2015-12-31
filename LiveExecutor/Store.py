# -*- coding: utf-8 -*-
u"""
Created on 2015-12-29

@author: cheng.li
"""

import pymssql
import pandas as pd
import h5py


conn = pymssql.connect('10.63.6.84', 'test', '12345678', 'datacenter_eqy')


def get_sql_conn():
    return pymssql.connect('10.63.6.84', 'test', '12345678', 'datacenter_eqy')


def get_all_the_trading_date(table_name):
    global conn
    sql = "select distinct(tradingDate) from {table_name} order by tradingDate".format(table_name=table_name)
    return pd.read_sql(sql, conn)


def data_loader_from_sql_server(trading_date, table_name):
    global conn
    template = """select tradingDate, tradingTime, instrumentID, openPrice, highPrice, lowPrice, closePrice, volume, turnover
        from {table_name}
        where tradingDate = '{trading_date}'
    """
    sql = template.format(table_name=table_name, trading_date=trading_date)
    return pd.read_sql(sql, conn)


def get_one_day_bar(trading_date, table_name):
    data = data_loader_from_sql_server(trading_date, table_name)
    data['timeStamp'] = data['tradingDate'] + ' ' + data['tradingTime']
    data = data.set_index('timeStamp')
    data.drop(['tradingTime'], axis=1, inplace=True)
    return data


def save_bar_to_hdf(data, hdf_file):
    grouped = data.groupby('tradingDate')
    for key, g in grouped:
        tag = key
        specific_data = g[['instrumentID', 'openPrice', 'highPrice', 'lowPrice', 'closePrice', 'volume', 'turnover']].sort_index()
        index = specific_data.index.values
        index.shape = index.size, 1
        index = index.astype('|S26')
        raw_data = specific_data.as_matrix()
        instruments = raw_data[:, 0].astype('|S9')
        data = raw_data[:, 1:].astype('float64')
        grp = hdf_file.create_group(tag)
        grp.create_dataset("time", data=index.tolist())
        grp.create_dataset("instrument", data=instruments.tolist())
        grp.create_dataset("data", data=data)
    return data


if __name__ == "__main__":
    import datetime as dt
    file_path, table_name = "d:/data/hdf5/equity_5min.hdf", "EQY_5MIN_PATCH"

    hdf_file = h5py.File(file_path, 'w')

    all_dates = get_all_the_trading_date(table_name)
    for trading_date in all_dates['tradingDate']:
        start = dt.datetime.now()
        data = get_one_day_bar(trading_date, table_name)
        save_bar_to_hdf(data, hdf_file)
        print(trading_date)
        print(dt.datetime.now() - start)

    hdf_file.close()


