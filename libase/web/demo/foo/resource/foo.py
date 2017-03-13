#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   foo.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

from flask_restful import (
    Resource,
)


class FooMixin(object):

    foos = {}


class FoosApi(Resource, FooMixin):

    def post(self):
        '''
        CREATE
        '''

        self

    def get(self):
        '''
        INDEX
        '''

        self


class FooApi(Resource, FooMixin):

    def get(self, _id):
        '''
        RETRIEVE
        '''

        self

    def put(self, _id):
        '''
        UPDATE
        '''

        self

    def delete(self, _id):
        '''
        DELETE
        '''

        self
