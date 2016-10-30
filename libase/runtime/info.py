#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   info.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import os
import sys


def get_current_file():
    '''
    获取当前代码文件名
    '''
    frame = sys._getframe(1)
    path = frame.f_globals.get('__file__')
    return os.path.abspath(path) if path else None


def get_current_module():
    '''
    获取当前模块对象
    '''
    frame = sys._getframe(1)
    module_name = frame.f_globals.get('__name__')
    return sys.modules[module_name]


def get_program_name():
    import __main__
    filename = getattr(__main__, '__file__', None)
    if filename is not None:
        filename = os.path.basename(filename)
        for postfix in ('.py', '.pyc'):
            if filename.endswith(postfix):
                filename = filename[:-len(postfix)]
    return filename
