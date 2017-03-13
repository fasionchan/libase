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

from collections import (
    Iterable,
)


class NULL(object):

    @classmethod
    def derive(cls):
        class NULL(cls):
            pass
        return NULL


def iterable(o):
    return isinstance(o, Iterable)


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


class PropertyDict(dict):

    @staticmethod
    def create_property(name):
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

    @classmethod
    def create_properties(cls, names):

        return {
            name: cls.create_property(name=name)
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


class ImmutableDictMixin(object):

    # 阉割
    for method in (
            '__delitem__',
            '__setitem__',
            'clear',
            'pop',
            'popitem',
            'setdefault',
            'update',
        ):

        locals().update(
            method=lambda *args, **kwargs: None,
        )


class AttrValuePairDict(PropertyDict, ImmutableDictMixin):

    PROPERTIES = [
        'attr',
        'value',
    ]

    locals().update(PropertyDict.create_properties(PROPERTIES))

    KEY_FUNC = staticmethod(lambda d: d['attr'])


class ListedPropertyDict(list):

    @staticmethod
    def create_property(attr, index=None):

        # TODO
        # Thread-Safe

        @property
        def getter(self):
            _index = index or self.attr2index[attr]

            return self[_index].value

        @getter.setter
        def setter(self, value):
            # 固定槽位
            if index is not None:
                self[index].attr = attr
                self[index].value = value
                return

            _index = self.attr2index.get(attr)
            if _index is not None:
                self[_index].attr = attr
                self[_index].value = value
                return

            pair = AttrValuePairDict()
            pair.attr = attr
            pair.value = value

            _index = len(self)
            self.append(pair)

            assert len(self) == _index + 1

            self.attr2index[attr] = _index

        @setter.deleter
        def deleter(self):
            # 固定槽位
            if index is not None:
                self[index].value = None
                return

            _index = self.attr2index.pop(attr)
            self.pop(_index)

        return deleter

    @classmethod
    def create_properties(cls, attrs):
        properties = {}
        for attr in attrs:
            index = None
            if isinstance(attr, (list, tuple)):
                attr, index = attr

            properties[attr] = cls.create_property(
                attr=attr,
                index=index,
            )

        return properties

    @property
    def attr2index(self):
        attr2index_attr = '_attr2index'

        attr2index = getattr(self, attr2index_attr, None)
        if attr2index is not None:
            return attr2index

        attr2index = {}
        for i, item in enumerate(self):
            attr2index[item['attr']] = i

        setattr(self, attr2index_attr, attr2index)

        return attr2index

    def __cmp__(self, other):
        key_func = AttrValuePairDict.KEY_FUNC
        return cmp(sorted(self, key=key_func), sorted(other, key=key_func))

    def __eq__(self, other):
        key_func = AttrValuePairDict.KEY_FUNC
        return sorted(self, key=key_func).__eq__(sorted(other, key=key_func))

    def __ne__(self, other):
        key_func = AttrValuePairDict.KEY_FUNC
        return sorted(self, key=key_func).__ne__(sorted(other, key=key_func))


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
