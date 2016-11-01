#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   thread_util.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import signal
import threading

from libase.platform.syscall import (
    get_thread_number,
    )


class ServeAsyncMixin(object):
    '''
    线程异步(并发)执行组件

    在serve_forever函数实现需要线程执行的逻辑，一般为循环处理某些任务，该组件
    提供底层线程初始化逻辑，调用serve_async函数便可完成启动线程。

    shutdown函数为通知线程退出，默认为设置运行标识self.running为假，
    serve_forever函数根据这个标识退出执行。shutdown可以根据serve_forever逻辑
    实现退出逻辑，比如往队列放进特殊标记数据等等。
    '''

    def setup_sigterm_self_join(self, args=(), kwargs={}):
        '''
        设置TERM信号自动触发回收线程
        '''

        def on_sigterm(*ignore):
            '''
            信号处理函数
            '''
            self.join(*args, **kwargs)

        # 注册信号处理函数
        signal.signal(signal.SIGTERM, on_sigterm)

    def setup_interruptible_sleep(self):
        '''
        设置可中断计时器组件
        '''

        self._sam_cancelled = threading.Event()
        def sleep(seconds):
            self._sam_cancelled.wait(seconds)
        self.sleep = sleep

    def setup_serve_async(self):
        self.setup_interruptible_sleep()

    def setup_thread_name(self, thread_name):
        '''
        设置执行线程名
        '''

        self._serve_thread.setName(thread_name)

    def serve_async(self, thread_name=None, args=(), daemon=True):
        '''
        启动线程执行serve_forever方法
        '''

        # 新建线程
        self._serve_thread = threading.Thread(
            target=self.serve_forever,
            args=args,
            )

        # 设置线程名
        if thread_name is not None:
            self.setup_thread_name(thread_name=thread_name)


        # 设置Daemon属性，影响退出行为
        self._serve_thread.setDaemon(daemon)

        # 启动线程开始执行
        self._serve_thread.start()

    def shutdown(self):
        self.running = False

    def join(self, timeout=None):
        '''
        回收执行线程
        '''

        # 通知线程退出
        self.shutdown()

        _sam_cancelled = getattr(self, '_sam_cancelled', None)
        if _sam_cancelled is not None:
            _sam_cancelled.set()

        _serve_thread = getattr(self, '_serve_thread', None)
        if _serve_thread:
            _serve_thread.join(timeout=timeout)
