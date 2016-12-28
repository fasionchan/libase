#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   oss_http.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import hashlib
import os

import oss2

from libase.server import (
    file_server,
)
from libase.util.decorator import (
    eval_now,
)
from libase.util.setting import (
    get_setting,
)


def default_file_namer(name, content):
    return hashlib.md5(content).hexdigest()


DEFAULT_CONFIGS = [
    {
        'path': '/',
        'prefix': 'uploaded',
        'namer': default_file_namer,
    },
]



def create_app(configs=DEFAULT_CONFIGS):
    bucket_name = get_setting('OSS_HTTP_BUCKET_NAME')
    assert bucket_name is not None

    access_key_id = get_setting('OSS_HTTP_ACCESS_KEY_ID')
    assert access_key_id is not None

    access_key_secret = get_setting('OSS_HTTP_ACCESS_KEY_SECRET')
    assert access_key_secret is not None

    endpoint = get_setting('OSS_HTTP_ENDPOINT')
    assert endpoint is not None

    name = get_setting('OSS_HTTP_APP_NAME', 'oss')
    assert name is not None

    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)

    def get_file_handler(prefix, namer):

        prefix = prefix.lstrip('/')

        def handler(name, file_object):
            # 类型后缀
            parts = name.split('.')
            type_postfix = '' if len(parts) == 1 else parts[1]

            # 文件内容
            content = file_object.read()

            # 名字后缀
            postfix = namer(name=name, content=content)
            if type_postfix:
                postfix = '.'.join((postfix, type_postfix))

            # OSS键
            key = os.path.join(prefix, postfix)

            # 保存
            bucket.put_object(key, content)

        return handler

    routes = {}
    for config in configs:
        path = config.get('path', '/')
        prefix = config.get('prefix', path).lstrip('/')
        namer = config.get('namer', default_file_namer)

        routes[path] = get_file_handler(
            prefix=prefix,
            namer=namer,
            )

    app = file_server.create_app(
        name=name,
        routes=routes,
    )

    return app


app = create_app()
