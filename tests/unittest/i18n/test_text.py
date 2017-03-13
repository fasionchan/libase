#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   test_text.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import itertools
import pytest

from libase.i18n.text import (
    Text,
    ListedText,
)


class TestText(object):

    def test(self):
        self


class TestListedText(object):

    TEXTS = [
        'a',
        u'b',
        '我',
        u'你',
    ]

    DEFAULT_CASES = itertools.combinations(TEXTS, 2)

    @pytest.mark.parametrize('text,another', DEFAULT_CASES)
    def test_default(self, text, another):
        t = ListedText()
        t.text = text
        assert t.text == text
        assert t.zh_cn == text
        assert t == [dict(attr='zh_cn', value=text)]

        t.text = another
        assert t.text == another
        assert t.zh_cn == another
        assert t == [dict(attr='zh_cn', value=another)]
