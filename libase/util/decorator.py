#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   decorator.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import os
import logging
import traceback
import functools


def call_now(func):
    '''
    立即调用修饰器
    调用被修饰函数。

    func - 被修饰函数
    '''

    func()

    return func


def eval_now(func):
    '''
    立即调用修饰器
    调用被修饰函数并回传结果。

    func - 被修饰函数
    '''

    return func()


def thread_safe(func):
    '''
    线程安全修饰器
    被修饰函数的调用将被一个锁所同步。

    func - 被修饰函数
    '''

    # 使用锁同步并发执行
    import threading
    lock = threading.Lock()

    @functools.wraps(func)
    def proxy_func(*args, **kwargs):
        ''' 修饰器代理函数 '''
        with lock:
            return func(*args, **kwargs)

    return proxy_func


def thread_safe_by_group_wrapper():
    '''
    thread_safe_by_group 函数包装器
    用闭包封装group_lock_mapping。
    '''
    group_lock_mapping = {}
    def thread_safe_by_group(group='default'):
        '''
        按组划分的线程安全修饰器产生器
        接收一个组名，返回一个修饰器，保护被修饰函数的多线程调用。
        注意，同一个组的修饰器共用一个锁。

        group - 组名
        '''
        import threading
        lock = group_lock_mapping.setdefault(group, threading.Lock())
        def thread_safe(func):
            '''
            线程安全修饰器
            被修饰函数的调用将被一个锁所同步。

            func - 被修饰函数
            '''
            def execute(*args, **kwargs):
                ''' 修饰器代理函数 '''
                with lock:
                    return func(*args, **kwargs)
            return execute
        return thread_safe
    return thread_safe_by_group

thread_safe_by_group = thread_safe_by_group_wrapper()
del thread_safe_by_group_wrapper


def catch_exc(func):
    '''
    异常捕获修饰器
    捕获函数执行抛出的异常并在日志输出函数名、异常详情

    func - 被修饰函数
    '''

    def execute(*args, **kwargs):
        ''' 修饰器代理函数 '''
        try:
            return func(*args, **kwargs)
        except Exception:
            logging.error('{module}.{func}(): {tb}'.format(
                module=func.func_globals.get('__name__', ''),
                func=func.__name__,
                tb=traceback.format_exc(),
                ))
    return execute


def catch_exc_quiet(func):
    '''
    异常捕获修饰器
    捕获函数执行抛出的异常，返回None

    func - 被修饰函数
    '''
    def execute(*args, **kwargs):
        ''' 修饰器代理函数 '''
        try:
            return func(*args, **kwargs)
        except Exception:
            return None
    return execute


def catch_exc_detail(func, limit=None):
    '''
    异常详情捕获修饰器
    捕获函数执行抛出的异常并在日志输出函数名、调用参数、异常详情

    func - 被修饰函数
    '''
    def execute(*args, **kwargs):
        ''' 修饰器代理函数 '''
        try:
            return func(*args, **kwargs)
        except Exception:
            logging.error('{module}.{func}(*{args}, **{kwargs}): {tb}'.format(
                module=func.func_globals.get('__name__', ''),
                func=func.__name__,
                args=str(args)[:limit] if limit else args,
                kwargs=str(kwargs)[:limit] if limit else kwargs,
                tb=traceback.format_exc(),
                ))
    return execute


def catch_exc_detail_limit(limit=1024):
    '''
    异常详情捕获修饰器
    捕获函数执行抛出的异常并在日志输出函数名、调用参数、异常详情

    size - 参数串长度限制
    '''

    def catch_exc_detail_limit(func):
        '''
        异常详情捕获修饰器
        捕获函数执行抛出的异常并在日志输出函数名、调用参数、异常详情

        func - 被修饰函数
        '''

        return catch_exc_detail(func, limit=limit)

    return catch_exc_detail_limit


def log_call_detail(func):
    '''
    函数调用详情修饰器

    func - 被修饰函数
    '''
    def execute(*args, **kwargs):
        ''' 修饰器代理函数 '''
        logging.debug('{module}.{func}(*{args}, **{kwargs})'.format(
            module=func.func_globals.get('__name__', ''),
            func=func.__name__,
            args=args,
            kwargs=kwargs,
            ))
        func(*args, **kwargs)
    return execute


def log_exc(func):
    '''
    异常打日志修饰器
    函数执行异常时在日志输出函数名、异常详情

    func - 被修饰函数
    '''
    def execute(*args, **kwargs):
        ''' 修饰器代理函数 '''
        try:
            return func(*args, **kwargs)
        except Exception:
            logging.error('{module}.{func}(): {tb}'.format(
                module=func.func_globals.get('__name__', ''),
                func=func.__name__,
                tb=traceback.format_exc(),
                ))
            raise
    return execute


def log_exc_detail(func):
    '''
    异常详情打日志修饰器
    函数执行异常时在日志输出函数名、调用参数、异常详情

    func - 被修饰函数
    '''
    def execute(*args, **kwargs):
        ''' 修饰器代理函数 '''
        try:
            return func(*args, **kwargs)
        except Exception:
            logging.error('{module}.{func}(*{args}, **{kwargs}): {tb}'.format(
                module=func.func_globals.get('__name__', ''),
                func=func.__name__,
                args=args,
                kwargs=kwargs,
                tb=traceback.format_exc(),
                ))
            raise
    return execute


def alarm_on_exc(func):
    def execute(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            catch_alarm(func, args, kwargs)
    return execute

def catch_exc_alarm_wait(func):
    def execute(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            catch_alarm(func, args, kwargs)
            print '-' * 60
            while True:
                cmd = raw_input('please input command (continue/stop): ')
                if cmd == 'continue':
                    print 'continue running...'
                    break
                elif cmd == 'stop':
                    os._exit(200)
                else:
                    continue
    return execute


def catch_alarm(func, args, kwargs):
    from .alarm import alarm as send_alarm
    error_msg = '{module}.{func}(*{args}, **{kwargs}): {traceback}'.format(
        module=func.func_globals.get('__name__', ''),
        func=func.__name__,
        args=args,
        kwargs=kwargs,
        traceback=traceback.format_exc(),
        )
    send_alarm(error_msg)


def alarm_exit_on_exc(func):
    ''' 异常报警并退出程序修饰器 '''
    def execute(*args, **kwargs):
        ''' 修饰器代理 '''
        try:
            return func(*args, **kwargs)
        except Exception, ex:
            catch_alarm(func, args, kwargs)
            os._exit(200)
    return execute


def exit_on_exc(func):
    '''
    异常详情捕获并退出程序修饰器
    捕获函数调用抛出的异常，在日志中输出异常详情并退出程序

    func - 被修饰函数
    '''
    def execute(*args, **kwargs):
        ''' 修饰器代理 '''
        try:
            return func(*args, **kwargs)
        except Exception, ex:
            logging.error('{module}.{func}(*{args}, **{kwargs}): {tb}'.format(
                module=func.func_globals.get('__name__', ''),
                func=func.__name__,
                args=args,
                kwargs=kwargs,
                tb=traceback.format_exc(),
                ))
            os._exit(200)
    return execute


def cache(timeout=3):
    """
    缓存调用方法
    :param timeout: 缓存时间
    :return:
    """
    f_cache = {}

    def source(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _id = id(func)
            last_ts, last_ret = f_cache[_id] if _id in f_cache else (0, None)
            ts = time.time()
            if ts - last_ts <= timeout:
                return last_ret
            ret = func(*args, **kwargs)
            f_cache[_id] = (ts, ret)
            return ret

        return wrapper

    return source


class ClassPropertyDescriptor(object):

    def __init__(self, fget, fset=None, fdel=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel

    def __get__(self, obj, cls=None):
        if cls is None:
            cls = type(obj)
        return self.fget.__get__(obj, cls)()

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError('can not set attribute')
        cls = type(obj)
        return self.fset.__get__(obj, cls)(value)

    def __delete__(self, obj):
        if not self.fset:
            raise AttributeError('can not delete attribute')
        cls = type(obj)
        return self.fdel.__get__(obj, cls)()


def classproperty(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)
    return ClassPropertyDescriptor(func)
