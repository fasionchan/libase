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
        self.book_by_id = self.book
        self.book_by_isbn = self.book.isbn

    def get_info_by_id(self, _id):
        return None

    def get_info_by_isbn(self, isbn):
        return self.book_by_isbn[isbn].get().json()

    def get_info(self, _id=None, isbn=None):
        if _id is not None:
            return self.get_info_by_id(_id=_id)

        if isbn:
            return self.get_info_by_isbn(isbn=isbn)
