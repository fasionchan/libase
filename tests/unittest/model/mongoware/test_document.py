#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   test_document.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import pytest
import random
import uuid

from bson import (
    ObjectId,
)
from pymongo import (
    MongoClient,
)
from pymongo.collection import (
    Collection,
)
from libase.model.mongoware.document import (
    MongoDocument,
)
from libase.util.helper import (
    args_kwargs,
)


class DemoDocument(MongoDocument):

    __collection__ = 'demo_doc'

    schema_config = {
        '_id': (ObjectId, dict(filler=lambda *args, **kwargs: ObjectId())),
        'name': unicode,
        'value': float,
    }


@pytest.fixture(scope='function')
def new_MD():
    MD = MongoDocument
    return type(MD.__name__, (MD,), {})


@pytest.fixture(scope='function')
def MD_with_db(new_MD, mongo_db):
    return new_MD.with_db(mongo_db, derive=True)


@pytest.fixture(scope='function')
def DD(mongo_db):
    return DemoDocument.with_db(mongo_db, derive=True)


class TestDocument(object):

    def test_with_db_uri(self, new_MD, mongodb_uri):
        MD = new_MD.with_db(db=mongodb_uri)

        assert MD.db
        assert isinstance(MD.db, MongoClient)

    def test_with_db_uri(self, new_MD, mongo_db):
        MD = new_MD.with_db(db=mongo_db)

        assert MD.db is mongo_db

    @pytest.mark.parametrize('derive', [True, False])
    def test_with_db_derive(self, new_MD, mongo_db, derive):
        MD = new_MD.with_db(mongo_db, derive=derive)
        if derive:
            assert MD is not new_MD
            assert MD is not MongoDocument
        else:
            assert MD is new_MD

    def test_with_default_coll(self, MD_with_db):
        assert MD_with_db.coll is not None
        assert isinstance(MD_with_db.coll, Collection)
        assert MD_with_db.coll.name == MD_with_db.__collection__

    def test_with_coll(self, MD_with_db):
        MD_with_db.with_coll('test1')

        assert isinstance(MD_with_db.coll, Collection)
        assert MD_with_db.coll.name == 'test1'

    SAVE_CASES = [
        (uuid.uuid4().get_hex(), random.random(), uuid.uuid4().get_hex(), random.random())
        for _ in xrange(3)
    ]

    @pytest.mark.parametrize('name1,value1,name2,value2', SAVE_CASES)
    def test_curd(self, DD, name1, value1, name2, value2):
        # Create
        doc1 = DD(dict(name=name1, value=value1))
        doc1.save()
        assert isinstance(doc1.get('_id'), ObjectId)

        # Retrieve
        doc2 = DD.find_one(args_kwargs(dict(name=name1)))
        assert doc2 == doc1

        # Update
        doc1['name'] = name2
        doc1.save()
        doc2 = DD.find_one(args_kwargs(dict(name=name2)))
        assert doc2 == doc1

        doc1['value'] = value2
        doc1.save()
        doc2 = DD.find_one(args_kwargs(dict(name=name2)))
        assert doc2 == doc1

        # Delete
        doc1.delete()

        doc2 = DD.find_one(args_kwargs(dict(name=name1)))
        assert doc2 is None
