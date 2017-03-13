#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   route.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

from . import (
    app,
    api,
)

from .resource.foo import (
    FoosApi,
    FooApi,
)

api.add_resource(
    FoosApi,
    '/foo',
)

api.add_resource(
    FooApi,
    '/foo/<string:_id>',
)
