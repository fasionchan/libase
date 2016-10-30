#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   codec.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import sys


def set_default_encoding(encoding='utf8'):
    import sys
    reload(sys)
    sys.setdefaultencoding(encoding)


def set_default_encoding_utf8():
    return set_default_encoding(encoding='utf8')
