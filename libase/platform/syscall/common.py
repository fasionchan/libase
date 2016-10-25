#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   common.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import ctypes
import ctypes.util

from libase.util.decorator import (
    call_now,
    catch_exc_quiet,
    )

@call_now
@catch_exc_quiet
def libc():
    name = ctypes.util.find_library('c')
    if not name:
        return None

    libc = ctypes.cdll.LoadLibrary(name)
    return libc
