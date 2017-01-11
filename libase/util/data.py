#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   data.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''


class DictAttrProxy(object):

    def __init__(self, data):
        self._dap_data = data

    def __getattribute__(self, name):
        if name == '_dap_data':
            return super(DictAttrProxy, self).__getattribute__(name)

        attr = self._dap_data.get(name, self)
        if attr is not self:
            return DictAttrProxy(attr)

        raise KeyError(name)

    def __getitem__(self, key_or_index):
        return DictAttrProxy(self._dap_data[key_or_index])


class DataInexistence(object):
    pass


def extract(data, path, quire=True, default=DataInexistence):
    if isinstance(path, basestring):
        path = path.split('.')

    for index in path:
        try:
            data = data[index]
        except:
            if quire:
                return default

            raise

    return data


def ensure_inexistence(data, pathes):
    for path in pathes:
        assert extract(data=data, path=path) is DataInexistence
