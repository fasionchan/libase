#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   fs.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import os
import stat

from collections import (
    defaultdict,
    )

from libase.runtime.info import (
    get_current_module,
    )

from .decorator import (
    eval_now,
    )


@eval_now
def reward_os_path():
    def create_handler(t):
        test_name = 'S_IS%s' % (t.upper(),)
        test = getattr(stat, test_name, None)
        if test is not None:
            def handler(path):
                return test(os.stat(path).st_mode)
            return handler

    self_module = get_current_module()
    for t in ('reg', 'dir', 'chr', 'blk', 'fifo', 'lnk', 'sock'):
        handler_name = 'is%s' % (t,)
        handler = getattr(os.path, handler_name, None)
        if handler is None:
            handler = create_handler(t)
            if handler:
                setattr(os.path, handler_name, handler)
        setattr(self_module, handler_name, handler)


def ensure_dir(path, quite=False):
    if quite:
        try:
            return ensure_dir(path, quite=False)
        except:
            return

    # 非安静模式，会抛异常
    items = [item for item in os.path.abspath(path).split('/') if item]
    path = '/'
    already_ensure = True
    for item in items:
        path = os.path.join(path, item)
        if os.path.exists(path):
            assert(os.path.isdir(path))
        else:
            os.mkdir(path)
            already_ensure = False

    return already_ensure


def cal_file_size(path):
    SECTOR_SIZE = 512

    if os.path.isdir(path):
        size = [os.stat(path).st_blocks * SECTOR_SIZE]
        def addup_file_size(arg, dirname, fnames):
            for fname in fnames:
                path = os.path.join(dirname, fname)
                size[0] += os.stat(path).st_blocks * SECTOR_SIZE
        os.path.walk(path, addup_file_size, None)
        return size[0]

    return os.stat(path).st_blocks * SECTOR_SIZE


@eval_now
def file_type():
    def get_nan_file_type():
        def file_type(path):
            return 'nan'
        return file_type

    def get_unix_file_type():
        file_type_map = {}
        for t in ('reg', 'dir', 'chr', 'blk', 'fifo', 'lnk', 'sock'):
            mode_name = 'S_IF%s' % (t.upper(),)
            mode = getattr(stat, mode_name, None)
            if mode is not None:
                file_type_map[mode] = t

        def file_type(path):
            return file_type_map.get(stat.S_IFMT(os.stat(path).st_mode), 'nan')

        return file_type

    S_IFMT = getattr(stat, 'S_IFMT', None)
    if S_IFMT is None:
        return get_nan_file_type()
    else:
        return get_unix_file_type()


def cal_file_amount(path):
    ft = file_type(path)
    file_amount = defaultdict(int, [(ft, 1)])

    if ft == 'dir':
        def addup_file_amount(arg, dirname, fnames):
            for fname in fnames:
                path = os.path.join(dirname, fname)
                ft = file_type(path)
                file_amount[ft] += 1
        os.path.walk(path, addup_file_amount, None)

    return file_amount
