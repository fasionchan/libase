#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   ntp.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import json
import os
import threading
import time

from libase.util.decorator import (
    catch_exc_detail,
)
from libase.util.log import (
    LoggerMaintainer,
)
from libase.util.fs import (
    ensure_dir,
)
from .system import (
    LocalTimer,
)


class NTPTimer(object):

    NTP_FIELDS = [
        'offset',
    ]

    SAVE_FIELDS = [
        'ntp_ts',
        'ntp_mts',
        'ntp_rts',
        'ntp_info',
    ]

    def __init__(self, ntp_domain='pool.ntp.org', ntp_version=3,
            path=None, match_acc=0.1, tries=3, try_delay=0.1, timeout=3600):

        self.ntp_domain = ntp_domain
        self.ntp_version = ntp_version
        self.ntp_args = (self.ntp_domain, self.ntp_version)

        self.path = path

        self.tries = tries
        self.try_delay = try_delay
        self.timeout = timeout

        # NTP客户端
        from ntplib import NTPClient
        self.ntp_client = NTPClient()

        # 日志
        self.logger_name = __name__ + self.__class__.__name__
        self.logger = LoggerMaintainer.create_logger(self.logger_name)

        # 本地计时器
        self.local_timer = LocalTimer(match_acc=match_acc)

        self.offset = None

        self.ntp_ts = None
        self.ntp_mts = None
        self.ntp_rts = None
        self.ntp_info = {}

        self.cur_rts = None

    @catch_exc_detail
    def save(self, path=None):
        path = path or self.path
        if path is None:
                return False

        info = {
            name: getattr(self, name, None)
            for name in self.SAVE_FIELDS
        }

        text = json.dumps(info)
        file(path, 'w').write(text)

        return True

    @catch_exc_detail
    def load(self, path=None):
        path = path or self.path
        if path is None:
                return False

        if not os.path.exists(path):
            return False

        text = file(path).read(102400)
        data = json.loads(text)

        for attr, value in data.iteritems():
            setattr(self, attr, value)
        for attr, value in self.ntp_info.iteritems():
            setattr(self, attr, value)

        return True

    def update(self, local_timer=None):
        if local_timer is None:
            local_timer = self.local_timer

        if self.ntp_ts is None:
            return False

        valid = local_timer.matched(
            last_ts=self.ntp_ts,
            last_mts=self.ntp_mts,
        )

        if valid:
            cur_rts = local_timer.cur_ts + self.offset
            if cur_rts - self.ntp_rts < self.timeout:
                self.cur_rts = cur_rts
            else:
                valid = False

        return valid

    @catch_exc_detail
    def request(self):
        # 获取本地时间
        self.local_timer.fetch()

        self.logger.debug(
            ('action', 'request_ntp'),
            ('args', self.ntp_args),
            ('start_ts', self.local_timer.cur_ts),
        )

        resp = self.ntp_client.request(*self.ntp_args)

        # 解析结果
        ntp_info = {
            name: getattr(resp, name, None)
            for name in self.NTP_FIELDS
        }

        # 再次获取本地时间
        self.local_timer.fetch()

        # 是否有效
        valid = self.local_timer.matched()

        if valid:
            for name, value in ntp_info.iteritems():
                setattr(self, name, value)

            self.cur_rts = self.local_timer.cur_ts + self.offset

            self.ntp_info = ntp_info
            self.ntp_ts = self.local_timer.cur_ts
            self.ntp_mts = self.local_timer.cur_mts
            self.ntp_rts = self.cur_rts

            self.resp =resp

        self.logger.debug(
            ('action', 'ntp_requested'),
            ('end_ts', self.local_timer.cur_ts),
            ('elapsed', self.local_timer.delta_mts),
            ('ntp_info', ntp_info),
            ('valid', valid),
        )

        return valid

    def request_with_retry(self):
        for _ in xrange(self.tries):
            if self.request():
                return True
        return False

    def fetch(self, block=True):
        while block:
            # 请求NTP
            if self.request_with_retry():
                return True

            time.sleep(self.try_delay)

        return False


class CachedNTPTimer(object):

    def __init__(self, workdir='/tmp/rtime_ntp_dont_rm/', ntp_tries=3,
            try_delay=0.1, match_acc=0.1, timeout=3600,
            ntp_domain='pool.ntp.org', ntp_version=3,
            block=True, degraded=False):

        # 工作目录(缓存结果)
        self.workdir = workdir
        ensure_dir(self.workdir)

        # 缓存文件分为
        # main_path 主文件
        # self_path 进(线)程文件
        # 先写进程文件，然后重命名到主文件，因此避免访问竞争态
        self.main_path = os.path.join(self.workdir, 'main')

        # 本地计时器
        self.local_timer = LocalTimer(match_acc=match_acc)

        # NTP计时器
        self.ntp_timer = NTPTimer(
            ntp_domain=ntp_domain,
            ntp_version=ntp_version,
            match_acc=match_acc,
            tries=ntp_tries,
            try_delay=try_delay,
            timeout=timeout,
        )

        self.block = block
        self.degraded = degraded

    @property
    def self_path(self):
        pid = os.getpid()
        thread_ident = threading.currentThread().ident

        # 进程号+线程号唯一确定一个写文件，避免冲突
        filename = '.'.join((str(pid), str(thread_ident)))
        path = os.path.join(self.workdir, filename)

        return path

    @property
    def _cur_rts(self):
        return self.ntp_timer.cur_rts

    @property
    def cur_rts(self):
        if self.fetch():
            return self._cur_rts
        elif self.degraded:
            return self.local_timer.cur_ts

    @property
    def _offset(self):
        return self.ntp_timer.offset

    @property
    def offset(self):
        if self.fetch():
            return self._offset
        elif self.degraded:
            return 0

    def fetch(self, block=None):
        if block is None:
            block = self.block

        # 获取本地时间
        self.local_timer.fetch()

        # 更新内存数据，测试有效
        if self.ntp_timer.update(local_timer=self.local_timer):
            return True

        # 加载缓存，测试有效
        if self.ntp_timer.load(path=self.main_path):
            if self.ntp_timer.update(local_timer=self.local_timer):
                return True

        # 请求NTP数据
        if self.ntp_timer.fetch(block=block):
            self.ntp_timer.save(path=self.self_path)
            os.rename(self.self_path, self.main_path)
            return True

        return False

    def get_cur_rts(self, block=None, degraded=None):
        if degraded is None:
            degraded = self.degraded

        if self.fetch(block=block):
            return self._cur_rts
        elif degraded:
            return self.local_timer.cur_ts

    def get_offset(self, block=None, degraded=None):
        if degraded is None:
            degraded = self.degraded

        if self.fetch(block=block):
            return self._offset
        elif degraded:
            return 0
