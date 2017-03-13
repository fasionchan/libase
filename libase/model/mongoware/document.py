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

from libase.client.uri2service import (
    uri2service,
)
from libase.util.data import (
    DictAttrProxy,
)
from libase.util.decorator import (
    classproperty,
)
from libase.util.helper import (
    args_kwargs,
)

from .schema import (
    Schema,
)


class MongoDocument(dict):

    __collection__ = 'test'

    __indexes__ = []

    @classmethod
    def ensure_coll_index(cls, coll):
        for index in cls.__indexes__:
            index = index.copy()
            keys = index.pop('keys')
            coll.create_index(keys, **index)

    @classmethod
    def inject_into(cls, other):
        setattr(other, cls.__name__, cls)

    @classproperty
    def schema(cls):
        schema_attr = '_schema'
        schema_config_attr = 'schema_config'

        schema = getattr(cls, schema_attr, None)
        if schema is not None:
            return schema

        schema_config = getattr(cls, schema_config_attr, None)
        schema = Schema.new(schema_config)

        setattr(cls, schema_attr, schema)

        return schema

    @classproperty
    def db(cls):
        db_attr = '_db'
        db_config_attr = '__database__'

        db = getattr(cls, db_attr, None)
        if db is not None:
            return db

        db_config = getattr(cls, db_config_attr, None)
        if db_config is None:
            return None

        db = uri2service(db_config)

        setattr(cls, db_attr, db)

        return db

    @classproperty
    def coll(cls):
        coll_attr = '_coll'
        coll_name_attr = '__collection__'

        coll = getattr(cls, coll_attr, None)
        if coll is not None:
            if isinstance(coll, basestring):
                db = getattr(cls, 'db', None)
                if db is None:
                    return None

                coll = getattr(db, coll)
                cls.ensure_coll_index(coll=coll)

                setattr(cls, coll_attr, coll)

            return coll

        coll_name = getattr(cls, coll_name_attr, None)
        if coll_name is None:
            return None

        db = getattr(cls, 'db', None)
        if db is None:
            return None

        coll = getattr(db, coll_name)
        cls.ensure_coll_index(coll=coll)

        setattr(cls, coll_attr, coll)

        return coll

    @classmethod
    def with_db(cls, db, derive=False):
        if isinstance(db, basestring):
            db = uri2service(db)

        if derive:
            return type(cls.__name__, (cls,), dict(_db=db))
        else:
            cls._db = db
            return cls

    @classmethod
    def with_coll(cls, coll, derive=False):
        if derive:
            return type(cls.__name__, (cls,), dict(_coll=coll))
        else:
            cls._coll = coll
            return cls

    @classmethod
    def find(cls, args_pair, instantiate=True, skip=None, limit=None):
        args, kwargs = args_pair
        cursor = cls.coll.find(*args, **kwargs)

        if skip:
            cursor = cursor.skip(skip)

        if limit:
            cursor = cursor.limit(limit)

        return [
            cls.instantiate(doc=doc) if instantiate else doc
            for doc in cursor
        ]

    @classmethod
    def find_one(cls, args_pair, instantiate=True):
        args, kwargs = args_pair
        doc = cls.coll.find_one(*args, **kwargs)
        if doc is None:
            return doc

        return cls.instantiate(doc=doc) if instantiate else doc

    @classmethod
    def find_random(cls):
        cls

    @classmethod
    def find_by_id(cls, _id):
        return cls.find_one(args_kwargs(query=dict(_id=_id)))

    @classmethod
    def instantiate(cls, doc):
        '''
        实例化文档对象
        '''

        return cls(doc=doc)

    def __init__(self, doc=None, coll=None):
        super(MongoDocument, self).__init__()

        self.assign(doc=doc)

        if coll is not None:
            self.coll = coll

    @property
    def proxy(self):
        proxy = getattr(self, '_proxy', None)
        if not proxy:
            self._proxy = proxy = DictAttrProxy(data=self)
        return proxy

    def assign(self, doc):
        self.clear()
        self.update(doc)

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

    def ensure_schema(self):
        return self.schema.ensure(
            parent=None,
            key=None,
            root=self,
            value=self,
        )

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

    def reload(self):
        # 主键
        _id = self.get('_id')
        if _id is None:
            return

        # 过滤条件
        _filter = {
            '_id': _id,
        }

        new = self.coll.find_one(
            filter=_filter,
        )

        # 更新内存数据
        if new:
            self.clear()
            self.update(new)
            return True

        return False

    def delete(self):
        # 主键
        _id = self.get('_id')
        if _id is None:
            return

        # 过滤条件
        _filter = {
            '_id': _id,
        }

        self.coll.delete_many(
            filter=_filter,
        )
