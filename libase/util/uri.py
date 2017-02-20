#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   url.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

from urllib import (
    urlencode,
)
from urlparse import (
    urlunparse,
)


def make_uri(netloc, scheme='http', path='', params='', query='', fragment=''):
    if not isinstance(query, basestring):
        query = urlencode(query)
    return urlunparse((scheme, netloc, path, params, query, fragment))
