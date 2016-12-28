#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   file_server.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import hashlib

from flask import (
    Flask,
    request,
)

from libase.util.log import (
    LoggerMaintainer,
    )


logger = LoggerMaintainer.create_logger(__name__)
LoggerMaintainer.create(__name__).basic_setup()


def default_file_handler(name, file_object):
    content = file_object.read()
    logger.info(
        ('action', 'new_file'),
        ('name', name),
        ('length', len(content)),
        ('hash', hashlib.md5(content).hexdigest()),
        )


def create_app(name='file_uploader', routes={'/': default_file_handler}):

    app = Flask(name)

    def set_up_route(path, handler):
        @app.route(path, methods=['POST'], endpoint=path)
        def upload_file():
            for name, file_object in request.files.iteritems():
                handler(name=name, file_object=file_object)
            return 'ok'

    for path, handler in routes.iteritems():
        set_up_route(path=path, handler=handler)

    return app
