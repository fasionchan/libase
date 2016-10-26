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


class Book(object):

    def __init__(self):
        self.uri_base = 'https://api.douban.com/v2'

        self.uri_book_isbn = '%s/book/isbn/%%s' % (self.uri_base,)

    def get_info_by_id(self, _id):
        return None

    def get_info_by_isbn(self, isbn):
        url = self.uri_book_isbn % (isbn,)
        print url
        return requests.get(url).json()

    def get_info(self, _id=None, isbn=None):
        if _id is not None:
            return self.get_info_by_id(_id=_id)

        if isbn:
            return self.get_info_by_isbn(isbn=isbn)
