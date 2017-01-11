#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   document.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

from bson import (
    ObjectId,
)
from pymongo.collection import (
    ReturnDocument,
)

from libase.util.data import (
    DictAttrProxy,
)


class MongoDocument(dict):

    @classmethod
    def with_coll(cls, coll):
        _coll = coll
        class MongoDocument(cls):
            coll = _coll
        return MongoDocument

    def __init__(self, doc=None, coll=None):
        if doc is not None:
            super(MongoDocument, self).__init__(doc)

        if coll is not None:
            self.coll = coll

    @property
    def proxy(self):
        proxy = getattr(self, '_proxy', None)
        if not proxy:
            self._proxy = proxy = DictAttrProxy(data=self)
        return proxy

    def compare_and_update(self, expected, update):
        # 过滤条件
        _filter = expected.copy()
        _filter['_id'] = self['_id']

        # 更新
        new = self.coll.find_one_and_update(
            filter=_filter,
            update=update,
            return_document=ReturnDocument.AFTER,
        )

        # 更新内存数据
        if new:
            self.clear()
            self.update(new)
            return True

        return False

    def compare_and_replace(self, expected, replacement):
        # 过滤条件
        _filter = expected.copy()
        _filter['_id'] = self['_id']

        # 替换
        new = self.coll.find_one_and_replace(
            filter=_filter,
            replacement=replacement,
            return_document=ReturnDocument.AFTER,
        )

        # 更新内存数据
        if new:
            self.clear()
            self.update(new)
            return True

        return False

    def save(self):
        # 主键
        _id = self.get('_id') or ObjectId()

        # 过滤条件
        _filter = {
            '_id': _id,
        }

        # 替换
        self.coll.find_one_and_replace(
            filter=_filter,
            replacement=self,
            upsert=True,
        )

        # 设置主键
        self.setdefault('_id', _id)
