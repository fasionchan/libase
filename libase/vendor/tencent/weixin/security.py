#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   security.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import os
import requests

from time import time as get_cur_ts

from base64 import (
    b64encode,
    )
from hashlib import (
    sha1,
    )

from libase.util.cache import (
    TimeCachedValueMixin,
    )
from libase.util.log import (
    LoggerMaintainer,
    )

logger = LoggerMaintainer.create_logger(__name__)


class AccessToken(TimeCachedValueMixin):

    def __init__(self, appid, secret):
        self.appid = appid
        self.secret = secret

        self.url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (self.appid, self.secret)

        self._value = None

    def fetch_value(self):
        logger.info(
            ('action', 'requesting_access_token'),
            ('url', self.url),
            )

        data = requests.get(self.url, verify=False).json()

        access_token = data.get('access_token')
        expires_in = data.get('expires_in', 0)

        return access_token, expires_in


class JsApiTicket(TimeCachedValueMixin):

    @staticmethod
    def js_sdk_sign(jsapi_ticket, noncestr, timestamp, url):
        text = ''.join([
            'jsapi_ticket=', jsapi_ticket,
            '&noncestr=', noncestr,
            '&timestamp=', str(int(timestamp)),
            '&url=', url,
            ])
        return sha1(text).hexdigest()

    def __init__(self, access_token):
        self.access_token = access_token

        self._value = None

    def fetch_value(self):
        url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi' % (self.access_token.value,)

        logger.info(
            ('action', 'requesting_jsapi_token'),
            ('url', url),
            )

        data = requests.get(url, verify=False).json()

        ticket = data.get('ticket')
        expires_in = data.get('expires_in', 0)

        return ticket, expires_in

    def sign_url(self, url, noncestr=None, timestamp=None):
        if noncestr is None:
            noncestr = b64encode(os.urandom(12))
        if timestamp is None:
            timestamp = str(int(get_cur_ts()))

        signature = self.js_sdk_sign(
            jsapi_ticket=self.value,
            noncestr=noncestr,
            timestamp=timestamp,
            url=url,
            )

        info = dict(
            timestamp=timestamp,
            noncestr=noncestr,
            signature=signature,
            url=url,
            )

        return info
