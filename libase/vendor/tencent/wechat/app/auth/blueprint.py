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

from libase.util.uri import (
    make_uri,
)
from libase.vendor.tencent.wechat.proto.auth import (
    WechatAuth,
)

_user_auth = None
wechat_auth = Blueprint('wechat_auth', __name__)


def verify_weixin_request(signature, timestamp, nonce, token):
    raw = [ensure_string(token), ensure_string(timestamp), ensure_string(nonce)]
    raw.sort()
    raw = ''.join(raw)
    return hashlib.sha1(raw).hexdigest() == signature


def tornado_verify_weixin_request(func):

    def handler(self):
        signature = self.get_argument('signature')
        timestamp = self.get_argument('timestamp')
        nonce = self.get_argument('nonce')
        token = 'CW3bTu81LxOhbTGgO3O7eqy9zlkWobRP'

        if not verify_weixin_request(signature, timestamp, nonce, token):
            return

        return func(self)

    return handler


def flask_verify_weixin_request(func):

    from flask import request
    from flask import current_app

    def handler():
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        token = current_app.config['WEIXIN_TOKEN']

        if not verify_weixin_request(signature, timestamp, nonce, token):
            return

        return func()

    return handler


def get_user_auth():
    global _user_auth
    if _user_auth is None:
        path = url_for('.on_redirect')
        redirect_uri = make_uri(
            netloc=current_app.config['WECHAT_AUTH_DOMAIN'],
            path=path,
        )

        _user_auth = WechatAuth(
            appid=current_app.config['APPID'],
            appsecret=current_app.config['APPSECRET'],
            redirect_uri=redirect_uri,
        )
    return _user_auth


@wechat_auth.route('/')
#@flask_verify_weixin_request
def echo():
    return request.args.get('echostr')

@wechat_auth.route('/init')
def initiate_auth():
    scope = request.args.get('scope', 'snsapi_base')
    state = request.args.get('state', '')

    user_auth = get_user_auth()

    uri = user_auth.get_auth_uri(
        scope=scope,
        state=state,
    )

    return redirect(uri)


@wechat_auth.route('/redirect')
def on_redirect():
    code = request.args.get('code')
    state = request.args.get('state', '')

    if code is not None:
        user_auth = get_user_auth()

        user_token = user_auth.fetch_access_token(
            code=code,
        )

        user_info = user_token.fetch_user_info()

        html = '<pre>' + json.dumps(user_info, ensure_ascii=False, indent=4) + '</pre>'

        return html

    return 'none'
