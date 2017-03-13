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

import os

from flask import (
    Flask,
)

from ..blueprint import (
    WechatAuthHandler,
)

app = application = Flask(__name__)


# TODO
def initiate_config():
    # 空配置
    app_config = {}

    try:
        import flask_config
        app_config = flask_config.app_config
    except:
        pass

    # 配置
    for name, value in app_config.iteritems():
        app.config[name] = value

    PREFIX = 'FLASK_CONFIG_'
    for name, value in os.environ.iteritems():
        if name.startswith(PREFIX):
            name = name[len(PREFIX):]
            app.config[name] = value
initiate_config()

app.register_blueprint(WechatAuthHandler().blueprint)
