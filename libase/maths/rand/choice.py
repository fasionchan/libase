#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   choice.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import random


def weighted_choice(weights, random_func=random.SystemRandom().random):
    # 权重浮点化
    weights = {
        name: float(weight)
        for name, weight in weights.iteritems()
    }

    # 求和
    total = sum(weights.values())

    # 随机挑一个浮点
    choiced = random_func()

    # 将权重映射到随机区间
    start = 0.
    for name, weight in weights.iteritems():
        # 区间结束
        end = start + weight / total

        # 区间判断
        if start <= choiced < end:
            return name

        # 下个区间开始
        start = end

    return name
