#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   gcs.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

from libase.util.data import (
    ImmutableDictMixin,
)


def _create_property(name):
    @property
    def getter(self):
        return super(GCS, self).setdefault(name, None)

    @getter.setter
    def setter(self, value):
        return super(GCS, self).__setitem__(name, value)

    @setter.deleter
    def deleter(self):
        return super(GCS, self).pop(name, None)

    return deleter


class GCS(dict, ImmutableDictMixin):

    PROPERTIES = [
        'longitude',
        'latitude',
        'altitude',
    ]

    def __init__(self, *args, **kwargs):
        super(GCS, self).__init__(*args, **kwargs)

        for field in self.PROPERTIES:
            super(GCS, self).setdefault(field, None)

        assert len(self) == len(self.PROPERTIES)

    for attr in PROPERTIES:
        locals().update(
            attr=_create_property(name=attr),
        )
