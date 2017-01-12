#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   mongo_counter.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

from pymongo.collection import (
    ReturnDocument,
)

from libase.model.mongoware.document import (
    MongoDocument,
)

class DuplicateName(Exception):
    pass


class MongoCounter(MongoDocument):

    def __init__(self, doc):
        # 主键
        _id = doc.get('_id')

        if _id is None:
            # 主键为空则为新文档，以文档为条件
            super(MongoCounter, self).__init__()

            self._filter = doc
            self._filter_good = False
        else:
            # 主键非空则为已存在文档，以主键为条件
            super(MongoCounter, self).__init__(doc)

            self._filter = {
                '_id': _id,
            }
            self._filter_good = True

    def inc(self, *names, **pairs):
        # 列表更新
        for name in names:
            if name in pairs:
                raise DuplicateName(name)
            pairs[name] = 1

        # 更新内容
        update = {
            '$inc': pairs,
        }

        new = self.coll.find_one_and_update(
            filter=self._filter,
            update=update,
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

        # 更新内存数据
        if new:
            self.clear()
            self.update(new)

        # 尝试将条件设置为主键
        if not self._filter_good:
            _id = self.get('_id')

            if _id is not None:
                self._filter = {
                    '_id': _id,
                }
                self._filter_good = True
