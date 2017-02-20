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
from ordereddict import (
    OrderedDict,
)

from libase.util.cache import (
    TimeCachedValueMixin,
)
from libase.util.log import (
    LoggerMaintainer,
)
from libase.util.uri import (
    make_uri,
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


class WechatAuth(object):

    def __init__(self, appid, appsecret, redirect_uri):
        self.appid = appid
        self.appsecret = appsecret
        self.redirect_uri = redirect_uri


    def get_auth_uri(self, scope='snsapi_base', state=''):
        query = OrderedDict()

        query['appid'] = self.appid
        query['redirect_uri'] = self.redirect_uri
        query['response_type'] = 'code'
        query['scope'] = scope
        query['state'] = state

        return make_uri(
            scheme='https',
            netloc='open.weixin.qq.com',
            path='/connect/oauth2/authorize',
            query=query,
            fragment='wechat_redirect',
        )

    def fetch_access_token(self, code):
        query = OrderedDict()

        query['appid'] = self.appid
        query['secret'] = self.appsecret
        query['code'] = code
        query['grant_type'] = 'authorization_code'

        uri = make_uri(
            scheme='https',
            netloc='api.weixin.qq.com',
            path='/sns/oauth2/access_token',
            query=query,
        )

        token_info = requests.get(uri).json()

        return UserAcessToken(
            wechat_auth=self,
            token_info=token_info,
        )


class UserAcessToken(object):

    def __init__(self, wechat_auth, token_info, lang='zh_CN'):

        self.wechat_auth = wechat_auth
        self.lang = lang

        self.set_token_info(token_info=token_info)

    def set_token_info(self, token_info):
        self.token_info = token_info
        self.unpack_token_info(**self.token_info)

    def unpack_token_info(self, access_token, expires_in, refresh_token,
            openid, scope, unionid=None):

        self.access_token = access_token
        self.expires_in = expires_in
        self.refresh_token = refresh_token
        self.openid = openid
        self.scope = scope
        self.unionid = unionid

    def test_access_token(self):
        query = OrderedDict()

        query['access_token'] = self.access_token
        query['openid'] = self.openid

        uri = make_uri(
            scheme='https',
            netloc='api.weixin.qq.com',
            path='/sns/auth',
            query=query,
        )

        #return uri

    def refresh_token(self):
        query = OrderedDict()

        query['appid'] = self.appid
        query['grant_type'] = 'refresh_token'
        query['refresh_token'] = self.refresh_token

        uri = make_uri(
            scheme='https',
            netloc='api.weixin.qq.com',
            path='/sns/oauth2/refresh_token',
            query=query,
        )

        return uri

    def fetch_user_info(self, lang=None):
        assert self.scope == 'snsapi_userinfo'

        query = OrderedDict()

        query['access_token'] = self.access_token
        query['openid'] = self.openid
        query['lang'] = lang or self.lang

        uri = make_uri(
            scheme='https',
            netloc='api.weixin.qq.com',
            path='/sns/userinfo',
            query=query,
        )

        userinfo = requests.get(uri).json()

        return userinfo
