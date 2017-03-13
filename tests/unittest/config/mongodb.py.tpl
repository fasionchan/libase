#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   mongodb.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

USER = ''
PASSWORD = ''
HOST = ''
PORT = 27017
DATABASE = ''

MONGODB_URI = 'mongodb://%s:%s@%s:%s/%s' % (
    USER,
    PASSWORD,
    HOST,
    PORT,
    DATABASE,
)
