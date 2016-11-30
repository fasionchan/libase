#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   book.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import requests

from libase.client.api_client import (
    ApiClient,
    )


class Book(object):

    API_BASE = 'https://api.douban.com/v2'

    def __init__(self, api_base=API_BASE):
        self.api_base = api_base
        self.api_client = ApiClient(api_base=self.api_base)

        self.book = self.api_client.book
        self.by_id = self.book
        self.by_isbn = self.book.isbn
        self.series = self.book.series

    def get_info_by_id(self, _id):
        return self.by_id[_id].get().json()

    def get_info_by_isbn(self, isbn):
        return self.by_isbn[isbn].get().json()

    def get_info(self, _id=None, isbn=None):
        if _id is not None:
            return self.get_info_by_id(_id=_id)

        if isbn:
            return self.get_info_by_isbn(isbn=isbn)

    def get_series_info(self, _id):
        return self.series[_id].get().json()

    def get_series_books(self, _id):
        return self.series[_id].books.get().json()
