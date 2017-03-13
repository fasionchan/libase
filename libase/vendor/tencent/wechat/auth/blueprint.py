#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   blueprint.py
Author:     Chen Yanfei
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import json

from flask import (
    Blueprint,
    current_app,
    redirect,
    request,
    url_for,
)

from libase.util.decorator import (
    cached_property,
)
from libase.util.uri import (
    make_uri,
)
from .common import (
    WechatAuth,
)


class WechatAuthHandler(object):

    def __init__(self, domain=None, appid=None, appsecret=None):
        self.domain = domain
        self.appid = appid
        self.appsecret = appsecret

    @cached_property(attr_name='_blueprint')
    def blueprint(self):
        blueprint = Blueprint('wechat_auth', __name__)

        blueprint.route('/init')(self.initiate_auth)
        blueprint.route('/redirect')(self.on_redirect)

        return blueprint

    @cached_property(attr_name='_wechat_auth')
    def wechat_auth(self):
        path = url_for('.on_redirect')
        redirect_uri = make_uri(
            netloc=self.domain or current_app.config['WECHAT_AUTH_DOMAIN'],
            path=path,
        )

        wechat_auth = WechatAuth(
            appid=self.appid or current_app.config['WECHAT_APPID'],
            appsecret=self.appsecret or current_app.config['WECHAT_APPSECRET'],
            redirect_uri=redirect_uri,
        )

        return wechat_auth

    def initiate_auth(self):
        '''
        URI: /init
        '''

        scope = request.args.get('scope', 'snsapi_base')
        state = request.args.get('state', '')

        uri = self.wechat_auth.get_auth_uri(
            scope=scope,
            state=state,
        )

        return redirect(uri)


    def on_redirect(self):
        '''
        URI: /redirect
        '''

        code = request.args.get('code')
        state = request.args.get('state', '')

        if code is not None:
            user_token = self.wechat_auth.fetch_access_token(
                code=code,
            )

            user_info = user_token.fetch_user_info()

            html = '<pre>' + json.dumps(user_info, ensure_ascii=False, indent=4) + '</pre>'

            return html

        return 'none'
