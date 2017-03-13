#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   test_mongo_address.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import pytest

from bson import (
    ObjectId,
)

from libase.i18n.text import (
    ListedText,
)
from libase.model.address.gcs import (
    GCS,
)
from libase.model.mongo_address import (
    MongoAddress,
)
from libase.util.helper import (
    args_kwargs,
)


def update_dict(dct, *args, **kwargs):
    dct.update(*args, **kwargs)
    return dct


class OtherType(object):
    pass


class TestMongoAddress(object):

    OTHER_TYPE = OtherType()

    GOOD_ADDRESS = {
        '_id': None,
        'parent': None,
        'ancestors': None,
        'type': 'known',
        'short': None,
        'long': None,
        'gcs': None,
        'extra': None,
    }

    GOOD_ADDRESS_FULL = {
        '_id': ObjectId(),
        'parent': ObjectId(),
        'ancestors': [ObjectId()],
        'type': 'known',
        'short': ListedText(),
        'long': ListedText(),
        'gcs': GCS(longitude=0, latitude=0, altitude=0),
        'extra': dict(detail=''),
    }

    GOOD_CASES = [
        GOOD_ADDRESS,
        GOOD_ADDRESS_FULL,
    ]

    @pytest.mark.parametrize('address', GOOD_CASES)
    def test_good(self, address):
        address = MongoAddress(address)
        assert address.ensure_schema()

    def test_id_filler(self):
        address = self.GOOD_ADDRESS.copy()
        address.pop('_id', None)
        address = MongoAddress(address)

        matched = address.ensure_schema()
        assert matched

        assert '_id' in address

    FIELD_TYPE_TEST_DATAS = [
        (update_dict(base.copy(), {field: OTHER_TYPE}), False)
        for base in (GOOD_ADDRESS, GOOD_ADDRESS_FULL)
        for field in base
    ]

    @pytest.mark.parametrize('address,matched', FIELD_TYPE_TEST_DATAS)
    def test_field_type(self, address, matched):
        address = MongoAddress(address)

        if matched:
            assert address.ensure_schema()
        else:
            assert not address.ensure_schema()

    def test_typical_case(self, mongo_db):
        # 派生绑定数据表
        MA = MongoAddress.with_coll('address', derive=True)
        MA.with_db(mongo_db)

        # 典型数据
        short = ListedText(zh_cn=u'广东')
        long = ListedText(zh_cn=u'广东省')
        gcs = GCS(longitude=1., latitude=2., altitude=3.)

        data = {
            'parent': None,
            'ancestors': None,
            'type': 'province',
            'short': short,
            'long': long,
            'gcs': GCS(longitude=0, latitude=2),
            'extra': {},
        }

        # 实例化对象并保存
        address = MA(data)
        address.save()

        # 确认生成主键ID
        _id = address.get('_id')
        assert isinstance(_id, ObjectId)

        # 确认数据已经保存
        raw = MA.find_one(args_kwargs(dict(_id=_id)), instantiate=False)
        assert raw == address

        # TODO
        # Check Custom Type
        address2 = MA.find_one(args_kwargs(dict(_id=_id)))
        assert address2 == address
