#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   console.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import sys
import code
import threading

from StringIO import StringIO

from libase.util.log import LoggerMaintainer

from libase.multirun.thread_util import (
    ServeAsyncMixin,
    get_thread_number,
    )

logger = LoggerMaintainer.create(__name__).logger


class OutputHookContext(object):

    def __enter__(self):
        self.sys_stdout = sys.stdout
        sys.stdout = self.stdout = StringIO()

        self.sys_stderr = sys.stderr
        sys.stderr = self.stderr = StringIO()

    def __exit__(self, *args, **kwargs):
        sys.stdout = self.sys_stdout
        sys.stderr = self.sys_stderr

    def getvalue(self):
        return '\n'.join([x for x in (self.stderr.getvalue(), self.stdout.getvalue(),) if x])


class ConsoleHandler(object):

    def __init__(self):
        self._interpreter = code.InteractiveInterpreter()
        self.lock = threading.RLock()
        self.stdio_hook = OutputHookContext()
        self.runsource('import __main__ as main')
        self.runsource('import sys')

    def runsource(self, source, filename="<input>", symbol="single"):
        with self.lock:
            with self.stdio_hook:
                more = self._interpreter.runsource(source, filename, symbol)
                if more:
                    # 需要更多输入
                    return True, ''
                else:
                    return more, self.stdio_hook.getvalue()


class ConsoleServer(ServeAsyncMixin):

    def __init__(self, addr='localhost', port=4444, code=''):
        self.addr = addr
        self.port = port
        self.code = code

    def serve_forever(self):
        logger.info(
            ('action', 'console_server_running'),
            ('tid', get_thread_number()),
            )

        # 启动终端解析器
        self._handler = ConsoleHandler()
        if self.code:
            self._handler.runsource(self.code)

        # 准备请求处理类
        from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
        class RequestHandler(SimpleXMLRPCRequestHandler):
            rpc_paths = ('/rConsole',)

        # 实例化server对象
        from SimpleXMLRPCServer import SimpleXMLRPCServer
        self._server = SimpleXMLRPCServer(
            (self.addr, self.port),
            requestHandler=RequestHandler,
            logRequests=False,
            )

        # 注册代码执行接口
        self._server.register_function(self._handler.runsource, "runsource")

        logger.info(
            ('action', 'xmlrpc_server_serving'),
            ('tid', get_thread_number()),
            )

        # 启动RPC服务
        self._server.serve_forever()


class ConsoleProxy(code.InteractiveConsole):

    def __init__(self, addr='localhost', port=4444):
        code.InteractiveConsole.__init__(self)
        self.addr = addr
        self.port = port
        self.connect()

    def connect(self):
        import xmlrpclib
        xmlrpc_uri = 'http://%s:%s/rConsole' % (self.addr, self.port,)
        self.proxy = xmlrpclib.ServerProxy(xmlrpc_uri)

    def runsource(self, source, filename="<input>", symbol="single"):
        more, output = self.proxy.runsource(source, filename, symbol)
        if output:
            self.write(output)
        return more


def start_console_server(port=4444, addr='localhost', code='',
        thread_name='ConsoleThread', startup=True):
    console_server = ConsoleServer(addr=addr, port=int(port), code=code)
    if startup:
        console_server.serve_async(thread_name=thread_name)
    return console_server


def run_console_proxy(port=4444, addr='localhost'):
    console_proxy = ConsoleProxy(addr=addr, port=int(port))
    console_proxy.runsource('''print 'Command: %s %s %s' % (sys.executable, getattr(main, '__file__', '__main__'), ' '.join(['"%s"' % (arg.replace('\\\\', '\\\\\\\\').replace('"', '\\\\"'),) for arg in sys.argv[1:]]),)\n''')
    console_proxy.interact()
