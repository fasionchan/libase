#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   divide.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import random


def divide_rp(interval, n, random_func=random.SystemRandom().random):
    used = 0.
    parts = []

    points = sorted([random_func() for x in xrange(n-1)])
    for point in points:
        using = interval * point

        part = using - used
        parts.append(part)

        used = using

    part = interval - used
    parts.append(part)

    return parts


def redivide(parts, total=None, random_func=random.SystemRandom().random):
    # 组成
    parts = [float(part) for part in parts]

    # 求和
    if total is None:
        total = sum(parts)

    # 比例
    factors = [part/total for part in parts]

    # 随机因子
    parts = [part*random_func() for part in parts]

    # 剩余量按比例
    extra = total - sum(parts)
    for i, factor in enumerate(factors):
        parts[i] += extra * factor

    return parts
