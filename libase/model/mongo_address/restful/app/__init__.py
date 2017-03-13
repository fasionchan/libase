#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   __init__.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import json

from bson import (
    ObjectId,
)
from flask import (
    Flask,
)
from flask_restful import (
    Api,
)

from libase.client.uri2service import (
    uri2service,
)
from libase.util.setting import (
    get_setting
)

from ..resource import (
    AddressesApi,
    AddressApi,
)
from ...model import (
    MongoAddress,
)

mongo_coll_uri = get_setting('MONGO_COLL_URI')
MongoAddress.with_coll(uri2service(mongo_coll_uri))

MongoAddress.inject_into(AddressesApi)
MongoAddress.inject_into(AddressApi)


class SmartJsonEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, ObjectId):
            return {'$oid': str(o)}
        elif isinstance(o, LocalProxy):
            return o._get_current_object()
        elif isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        return super(SmartJsonEncoder, self).default(o)

# 应用对象
app = application = Flask(__name__)

# 配置restful json样式
app.config['RESTFUL_JSON'] = {
    'separators': (', ', ': '),
    'indent': 4,
    'cls': SmartJsonEncoder,
}

# API对象
api = Api(
    app=app,
    prefix='/api/v1',
)

api.add_resource(
    AddressesApi,
    '/address',
)

api.add_resource(
    AddressApi,
    '/address/<string:_id>',
)
