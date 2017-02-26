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


class NULL(object):

    @classmethod
    def derive(cls):
        class NULL(cls):
            pass
        return NULL


def combine_dicts(*dcts):
    dct = dcts[0].copy()
    for _dct in dcts[1:]:
        dct.update(_dct)
    return dct


def alias_dict_items(dct, aliases):
    null = NULL()
    for dst, src in aliases.iteritems():
        value = dct.get(src, null)
        if value is not null:
            dct[dst] = value


def get_dict_property(name):
    @property
    def getter(self):
        return self[name]

    @getter.setter
    def setter(self, value):
        self[name] = value

    @setter.deleter
    def deleter(self):
        self.pop(name, None)

    return deleter


def get_dict_properties(names):

    return {
        name: get_dict_property(name=name)
        for name in names
    }


def FixedPropertyDict(names, aliases=None):

    class FixedPropertyDict(dict):

        locals().update(get_dict_properties(names=names))

        if aliases is not None:
            alias_items(locals(), aliases=aliases)

    return FixedPropertyDict


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
