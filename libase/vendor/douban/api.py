#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   api.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

from libase.client.api_client import (
    ApiClient,
    )

class DoubanApi(object):

    API_BASE = 'https://api.douban.com/v2'

    def __init__(self, api_base=API_BASE):
        self.api_base = api_base
        self.api_client = ApiClient(api_base=self.api_base)

        # 图书
        self.book = self.api_client.book
        self.book_by_isbn = self.book.isbn
