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

from flask import (
    Flask,
)

from flask_restful import (
    Api,
)

# 应用对象
app = application = Flask(__name__)

# API对象
api = Api(
    app=app,
    prefix='/api/v1',
)

import route
