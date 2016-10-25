#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   __init__.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

from libase.platform.common import OS

from .common import (
    libc,
    )

if OS == 'linux':
    from .linux import gettid as get_thread_number
elif OS == 'freebsd':
    from .freebsd import thr_self as get_thread_number
else:
    get_thread_number = lambda : None
