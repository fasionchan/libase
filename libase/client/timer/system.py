#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   system.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

from time import time as get_cur_ts
from monotonic import monotonic as get_cur_mts


class LocalTimer(object):

    '''

    '''

    def __init__(self, match_acc=0.1):
        self.match_acc = match_acc

        self.last_ts = None
        self.last_mts = None

        self.cur_ts = None
        self.cur_mts = None

    @property
    def delta_ts(self):
        if self.last_ts is None:
            return None

        return self.cur_ts - self.last_ts

    @property
    def delta_mts(self):
        if self.last_mts is None:
            return None

        return self.cur_mts - self.last_mts

    def fetch(self):
        # 保存上一次值
        if self.cur_ts is not None:
            self.last_ts = self.cur_ts
            self.last_mts = self.cur_mts

        # 获取本地时间
        self.cur_ts = get_cur_ts()
        self.cur_mts = get_cur_mts()

    def matched(self, last_ts=None, last_mts=None):
        '''
        (逝去)本地时间和内核单调时间是否一致
        '''

        # 默认与上次获取时间对比
        if last_ts is None:
            last_ts = self.last_ts
        if last_mts is None:
            last_mts = self.last_mts

        # 时间差
        delta_ts = self.cur_ts - last_ts
        delta_mts = self.cur_mts - last_mts

        # 不符合条件场景包括
        # 1 机器重启
        # 2 机器修改时间
        return abs(delta_ts-delta_mts) < self.match_acc
