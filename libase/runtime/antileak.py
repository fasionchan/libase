#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   antileak.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import objgraph
import random


def show_type_instance_random(type_name):
    # 类型名及图片输出路径
    type_name = str(type_name)
    filename = '/tmp/%s.png' % (type_name,)

    # 取出所有实例
    instances = objgraph.by_type(type_name)
    if not instances:
        return

    # 随机取出一个实例
    instance = random.choice(instances)

    # 画反向引用图
    objgraph.show_backrefs([instance], filename=filename)
