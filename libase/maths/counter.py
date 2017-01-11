#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   counter.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

from collections import (
    defaultdict,
)


class BaseCounter(object):

    '''
    (基础)计数器
    '''

    def __init__(self, value=0):
        self.value = value

    def get_value(self):
        return self.value

    def increase(self, inc=1):
        self.value += inc

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return str(self.value)


class BoundedCounter(BaseCounter):

    '''
    可限制最大值计数器
    '''

    # 最大值32位整数
    MAXIMUM = 0xffffffff

    @classmethod
    def derive(cls, maximum):
        '''

        '''
        class BoundedCounter(cls):
            MAXIMUM = maximum
        return BoundedCounter

    def __init__(self, value=0, maximum=None):
        if maximum is None:
            maximum = self.MAXIMUM

        super(BoundedCounter, self).__init__(value=value)
        self.maximum = maximum

    def increase(self, inc=1):
        value = self.value + inc
        if value > self.maximum:
            value -= self.maximum

        self.value = value


class MaskedCounter(BaseCounter):

    '''
    固定长度(掩码决定)计数器
    '''

    # 掩码
    MASK = 0xffffffff

    @classmethod
    def derive(cls, mask):
        '''
        派生子类拥有不同
        '''
        class MaskedCounter(cls):
            MASK = mask
        return MaskedCounter

    def __init__(self, value=0, mask=None):
        if mask is None:
            mask = self.MASK

        super(MaskedCounter, self).__init__(value=value)
        self.mask = mask

    def increase(self, inc=1):
        self.value = (self.value + inc) & self.mask


class CounterSet(object):

    '''
    计数器集
    '''

    def __init__(self, counter_class=MaskedCounter):
        self.counters = defaultdict(counter_class)

    def increase(self, name, inc=1):
        self.counters[name].increase(inc=inc)

    def dictify(self):
        data = {
            name: counter.get_value()
            for name, counter in self.counters.iteritems()
        }
        return data
