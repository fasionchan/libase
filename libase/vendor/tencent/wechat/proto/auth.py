#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   auth.py
Author:     Chen Yanfei
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import requests

from ordereddict import (
    OrderedDict,
)

from libase.util.log import (
    LoggerMaintainer,
)
from libase.util.uri import (
    make_uri,
)

logger = LoggerMaintainer.create_logger(__name__)


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
