#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   freebsd.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import ctypes
import ctypes.util

from libase.util.decorator import (
    catch_exc_detail,
    )

from .common import libc


@catch_exc_detail
def thr_self():
    if not libc:
        return

    # 整型及其指针
    thr_id_type = ctypes.c_long
    thr_id_type_p = ctypes.POINTER(thr_id_type)

    # ID值
    thr_id = thr_id_type(-1)
    libc.thr_self(thr_id_type_p(thr_id))

    return thr_id.value
