#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   cache.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

from monotonic import monotonic as get_cur_mts


class TimeCachedValueMixin(object):

    def sync_value(self):
        # 当前时间
        cur_mts = get_cur_mts()

        value, expires_in = self.fetch_value()

        self._value = value
        self._expired_mts = cur_mts + expires_in

        return self._value

    @property
    def value(self):
        # 当前时间
        cur_mts = get_cur_mts()

        if self._value is not None:
            if cur_mts < self._expired_mts:
                return self._value

        return self.sync_value()
