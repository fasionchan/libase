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


def get_max_type_instance(type_name):
    # 取出所有实例
    instances = objgraph.by_type(type_name)
    if not instances:
        return

    # 临时记录最大大小
    maxsize = 0
    max_one = None

    # 遍历实例
    for instance in instances:
        size = len(instance)
        if size > maxsize:
            maxsize = size
            max_one = instance

    return max_one


def show_type_max_instance(type_name):
    # 类型名及图片输出路径
    type_name = str(type_name)
    filename = '/tmp/max_%s.png' % (type_name,)

    # 找出最大实例
    max_one = get_max_type_instance(type_name=type_name)

    # 反向引用图
    objgraph.show_backrefs([max_one], filename=filename)
