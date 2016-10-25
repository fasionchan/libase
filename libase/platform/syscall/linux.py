#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   linux.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import os

from libase.util.decorator import (
    catch_exc_detail,
)

from .common import libc


@catch_exc_detail
def gettid():
    tid = libc.syscall(186)
    return tid


@catch_exc_detail
def tgkill(tgid, tid, sig):
    return libc.syscall(234, tgid, tid, sig)


@catch_exc_detail
def tkill(tid, sig):
    return tgkill(os.getpid(), tid, sig)
