#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   model.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import pymongo

from bson import (
    ObjectId,
)

from libase.i18n.text import (
    ListedText,
)
from libase.model.address.gcs import (
    GCS,
)
from libase.model.mongoware.document import (
    MongoDocument,
)


class MongoAddress(MongoDocument):

    schema_config = {
        '_id': (ObjectId, dict(filler=lambda *args, **kwargs: ObjectId())),

        # 父节点
        'parent': ObjectId,

        # 祖先节点
        'ancestors': [ObjectId],

        # 地址类型(层次)
        'type': (basestring, dict(nullable=False)),

        # 简称
        'short': ListedText,

        # 全称
        'long': ListedText,

        # 地理坐标
        'gcs': GCS,

        # 额外信息
        'extra': dict,
    }

    __indexes__ = [
        {
            'keys': [
                ('short.value', pymongo.ASCENDING),
            ],
        },
        {
            'keys': [
                ('long.value', pymongo.ASCENDING),
            ],
        },
    ]
