#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   theory.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import pyprimes


def first_prime_above(x):
    return pyprimes.primes_above(x).next()


def last_prime_below(x):
    for x in xrange(x, 0, -1):
        if pyprimes.is_prime(x):
            return x
