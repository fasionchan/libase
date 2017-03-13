#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   resource.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import flask

from bson import (
    ObjectId,
)
from flask import (
    request,
)
from flask_restful import (
    Resource,
)

from libase.util.helper import (
    args_kwargs,
)


class AddressesApi(Resource):

    def get(self):
        parent_id = request.args.get('parent_id')
        limit = int(request.args.get('limit', 10))
        skip = int(request.args.get('skip', 0))

        query = {}

        if parent_id:
            query['parent'] = ObjectId(parent_id)

        return self.MongoAddress.find(
            args_kwargs(query=query),
            skip=skip,
            limit=limit,
        )


class AddressApi(Resource):

    def get(self, _id):
        _id = ObjectId(_id)

        return self.MongoAddress.find_by_id(_id=_id)
