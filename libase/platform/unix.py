#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   unix.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import os
import sys

from multiprocessing import (
    Queue,
)


def get_init_process_id():

    # 队列用于与孙子进程通讯
    queue = Queue()

    def child_routine():
        '''
        子进程执行体
        '''

        def child_routine():
            '''
            孙子进程执行体
            '''

            # 等待主进程通知(父进程已退出)
            queue.get()
            # 回传父进程ID(即init进程ID)
            queue.put(os.getppid())

            sys.exit(0)

        # 在子进程中启动孙子进程
        child = os.fork()
        if child == 0:
            return child_routine()

        sys.exit(0)

    # 启动子进程
    child = os.fork()
    if child == 0:
        return child_routine()

    # 等待子进程退出，孙子进程成孤儿托孤给init
    os.waitpid(child, 0)

    # 通知孙子进程获取父进程ID
    queue.put(None)

    return queue.get()


if __name__ == '__main__':
    print get_init_process_id()
