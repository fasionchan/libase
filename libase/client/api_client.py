#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   api_client.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import requests

from urllib import (
    quote_plus,
    urlencode,
    )


class ApiClient(object):

    def __init__(self, api_base, pathes=[], kwargs={}):
        self.api_base = api_base
        self.pathes = pathes
        self.kwargs = kwargs

    @property
    def url(self):
        path = '/'.join([quote_plus(path) for path in self.pathes])
        qs = urlencode(self.kwargs)
        if qs:
            url = '%s/%s?%s' % (self.api_base, path, qs)
        else:
            url = '%s/%s' % (self.api_base, path)
        return url

    def __getattr__(self, name):
        pathes = self.pathes + [name]
        return self.__class__(
            api_base=self.api_base,
            pathes=pathes,
            )

    def __getitem__(self, name):
        pathes = self.pathes + [name]
        return self.__class__(
            api_base=self.api_base,
            pathes=pathes,
            )

    def options(self, **kwargs):
        return self.__class__(
            api_base=self.api_base,
            pathes=self.pathes,
            kwargs=kwargs,
            )

    def get(self):
        return requests.get(self.url)

    def post(self):
        return

    def put(self):
        return

    def delete(self):
        return

if __name__ == '__main__':
    api = ApiClient(
        api_base='https://api.douban.com/v2',
        )
    print api.book.isbn['9787505715660'].get().json()
