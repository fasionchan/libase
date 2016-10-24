#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   setup.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

VERSION = '1.0'

from setuptools import (
    setup,
    )

setup(
    name='libase',
    version=VERSION,
    author='Fasion Chan',
    author_email='fasionchan@gmail.com',
    packages=[
        'libase',
        'libase.multirun'
        ],
    scripts=[
        ],
    package_data={
        },
    install_requires=[
        ],
    )
