#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   uri2service.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Usage:
    uri2service('schema://uesrname:password@host:port/path1/path2?arg1=value1&arg2=value2')

    uri2service('mysql://test:test@127.0.0.1:3306/test?charset=utf8&use_unicode=False&cursorclass=DictCursor')
    uri2service('redis://127.0.0.1:6379/0')

Changelog:

'''

import urllib

from copy import deepcopy
from urlparse import urlparse, parse_qsl

from libase.util.decorator import (
    eval_now,
    catch_exc_quiet,
    )


def uriparse(uri):
    params = urlparse(uri)
    params.peer = '%s:%s' % (params.hostname, params.port) if params.port \
            else params.hostname
    params.args = map(urllib.unquote_plus, params.path.split('/')[1:])
    params.kwargs = dict(parse_qsl(params.query))
    return params


@eval_now
class uri2service(object):

    def __init__(self):
        self.schema_supported = {}

        self.setup_mysqldb()
        self.setup_mongodb()
        self.setup_redis()

    @catch_exc_quiet
    def setup_mysqldb(self):
        import MySQLdb
        import MySQLdb.cursors

        self.schema_supported['mysql'] = (
            MySQLdb.connect,
            {
                'host': 'hostname',
                'port': 'port',
                'user': 'username',
                'passwd': 'password',
                'db': 'args',
                'use_unicode': 'kwargs',
                'cursorclass': 'kwargs',
                '__kwargs__': 'kwargs'
                },
            {
                'port': lambda port: port or 3306,
                'db': lambda args: args[0],
                'use_unicode': lambda kwargs: eval(kwargs.get('use_unicode', 'True')),
                'cursorclass': lambda kwargs: getattr(MySQLdb.cursors, kwargs.get('cursorclass', 'Cursor')),
                },
            None,
            )

    def setup_mongodb(self):
        def mongodb_initor(inst, params):
            username = params.username
            if username:
                db = 'admin'
                if '.' in username:
                    db, username = username.split('.', 1)
                getattr(inst, db).authenticate(username, params.password)
            for item in params.args[:2]:
                inst = getattr(inst, item)
            return inst

        import pymongo
        self.schema_supported['mongodb'] = (
            pymongo.MongoClient,
            {
                'host': 'hostname',
                'port': 'port',
                },
            {
                'port': lambda port: port or 27017,
                },
            mongodb_initor,
            )

    @catch_exc_quiet
    def setup_redis(self):
        import redis

        self.schema_supported['redis'] = (
            redis.client.StrictRedis,
            {
                'host': 'hostname',
                'port': 'port',
                'db': 'args',
                },
            {
                'port': lambda port: port or 6379,
                'db': lambda args: args[0],
                },
            None,
            )

    def __call__(self, uri, scheme_conf=None, **kwargs):
        '''
        uri2service - 通过服务URI初始化服务库实例

        用法：
            uri2service('schema://uesrname:password@host:port/path1/path2?arg1=value1&arg2=value2')

        用法示例：
            uri2service('mysql://test:test@127.0.0.1:3306/test?charset=utf8&use_unicode=False&cursorclass=DictCursor')
            uri2service('redis://127.0.0.1:6379/0')
        '''

        # 解析URI参数
        params = uriparse(uri)

        # 模式(服务类型)
        scheme = params.scheme
        scheme_conf = scheme_conf or self.schema_supported.get(scheme)
        if not scheme_conf:
            raise Exception('no scheme conf')

        # 连接类，参数映射，参数转型，初始化函数
        cls, mapping, converts, init = scheme_conf
        mapping = deepcopy(mapping)
        converts = deepcopy(converts)

        # 连接初始化参数
        all_kwargs = getattr(params, mapping.pop('__kwargs__', '__nosuch__'), {})
        for dst, src in mapping.iteritems():
            value = getattr(params, src, None)
            convert = converts.get(dst)
            all_kwargs[dst] = convert(value) if convert else value

        # 来自调用的关键字参数
        all_kwargs.update(kwargs)

        inst = cls(**all_kwargs)
        if init:
            result = init(inst, params)
            if result is not None:
                return result

        return inst
