#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   setting.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import os

try:
    import settings
except:
    from . import fake_settings as settings


def get_setting(name, default=None):
    # 环境变量
    setting = os.environ.get(name)
    if setting:
        return setting

    # 配置
    setting = getattr(settings, name, default)
    return setting
