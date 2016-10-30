#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   helper.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''



def args(*args):
    return args


def kwargs(**kwargs):
    return kwargs


def args_kwargs(*args, **kwargs):
    return args, kwargs


def none_default(obj, default=None):
    return default if obj is None else obj


def first_or_default(list_object, default=None):
    return list_object[0] if list_object else default

first_or_none = first_or_default


def last_or_default(list_object, default=None):
    return list_object[-1] if list_object else default


last_or_none = last_or_default


def getitem(data, key, default):
    try:
        return data[key]
    except IndexError:
        return default
    except KeyError:
        return default
