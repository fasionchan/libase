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

import platform

OS = platform.system().lower()
if OS.startswith('cygwin'):
    OS = 'cygwin'
