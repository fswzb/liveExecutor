# -*- coding: utf-8 -*-
u"""
Created on 2015-12-29

@author: cheng.li
"""

import h5py
import numpy as np
from abc import ABCMeta
from abc import abstractmethod
import bisect


class DataProvider(object):

    __metaclass__ = ABCMeta

    """
    数据接口的抽象
    """

    @abstractmethod
    def quotes(self, instruments, timestamp):
        raise NotImplementedError()


class HDFDataProvider(DataProvider):

    def __init__(self, store_path):
        self.store_file = h5py.File(store_path, mode='r')
        self.current_cache = np.zeros(0)
        self.cached_date = None
        self.cached_merger = []
        self.current_filtered_cache = np.zeros(0)
        self.current_index = None
        self.all_instruments = None
        self.all_times = None
        self.current_names = None

    def quotes(self, instruments, time_stamp):
        date = time_stamp.__str__()[:10]
        if self.current_cache.size == 0 \
                or self.cached_date != date:
            try:
                file_handler = self.store_file[date]
                self.current_cache = file_handler['data'][:]
                self.all_instruments = file_handler['instrument'][:]
                self.all_times = file_handler['time'][:]
                filter_flag = np.in1d(self.all_instruments, instruments)
                self.current_filtered_cache = self.current_cache[filter_flag]
                self.current_index = self.all_times[filter_flag]
                self.current_names = self.all_instruments[filter_flag]
                self.cached_merger = instruments
            except KeyError:
                return None
            self.cached_date = date
            print("{0}'s data has been loaded".format(date))
        elif self.cached_merger is not instruments:
            filter_flag = np.in1d(self.all_instruments, instruments)
            self.current_filtered_cache = self.current_cache[filter_flag]
            self.current_index = self.all_times[filter_flag]
            self.current_names = self.all_instruments[filter_flag]
            self.cached_merger = instruments

        time_stamp = time_stamp.encode('ascii')
        left = bisect.bisect_left(self.current_index, time_stamp)
        right = bisect.bisect_right(self.current_index, time_stamp)
        return self.current_index[left], self.current_names[left:right], self.current_filtered_cache[left:right]


if __name__ == "__main__":

    from DataAPI import api
    from AlgoTrading.api import set_universe

    universe = [str(s[:6]) for s in set_universe('000300.zicn')]

    data = api.GetEquityBarMin5('600000', '2012-01-01', '2015-12-28')
    date_index = data.index

    store = HDFDataProvider('d:/data/hdf5/equity_5min.hdf')

    import datetime as dt
    start = dt.datetime.now()
    for date in date_index:
        data = store.quotes(universe, date.strftime("%Y-%m-%d %H:%M:%S.%f"))
    print(dt.datetime.now() - start)