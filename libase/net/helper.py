#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   helper.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

from socket import (
    socket,
    gethostbyaddr,
    AF_INET,
    SOCK_DGRAM,
    )


def get_ip():
    udp = socket(AF_INET, SOCK_DGRAM)
    udp.connect(('8.8.8.8', 8))
    return udp.getsockname()[0]


def get_hostname(ip):
    try:
        return gethostbyaddr(ip)[0]
    except Exception, error:
        return
