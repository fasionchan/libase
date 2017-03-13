#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   mongodb.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import pytest

from libase.client.uri2service import (
    uri2service,
)

from config.mongodb import (
    MONGODB_URI,
)


@pytest.fixture
def mongodb_uri():
    return MONGODB_URI


@pytest.fixture
def mongo_db(mongodb_uri):
    return uri2service(mongodb_uri)


@pytest.fixture
def mongo_coll(mongo_db):
    return mongo_db.test
