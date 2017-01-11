#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   mongo_qrcode.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

from bson import (
    Binary,
    ObjectId,
)
from qrcode import (
    QRCode,
)
from StringIO import (
    StringIO,
)

from libase.model.mongoware.document import (
    MongoDocument,
)


class MongoQRCode(MongoDocument):

    DEFAULT_GENERATOR = staticmethod(lambda x: str(x['_id']))
    DEFAULT_QRCODE_OPTIONS = {}

    generator = DEFAULT_GENERATOR
    qrcode_options = DEFAULT_QRCODE_OPTIONS

    @classmethod
    def with_options(cls, generator=None, qrcode_options=None):
        _generator, _qrcode_options = generator, qrcode_options

        class MongoQRCode(cls):
            if _generator:
                generator = staticmethod(_generator)

            if _qrcode_options is not None:
                qrcode_options = _qrcode_options

        return MongoQRCode

    def __init__(self, doc=None):
        super(MongoQRCode, self).__init__(doc)

        if '_id' not in self:
            self.create()

    def generate_image(self, value, _type='png'):
        qr = QRCode(**self.qrcode_options)
        qr.add_data(value)
        qr.make(fit=True)

        image = qr.make_image()

        stream = StringIO()
        image.save(stream, format=_type)

        return stream.getvalue()

    def create(self):
        self['_id'] = ObjectId()
        self.render()
        self.save()

    def render(self):
        # 值
        value = self.generator(self)
        self['value'] = value

        # 生成图像
        image = self.generate_image(value=value)
        self['image'] = Binary(image)
        print repr(image), len(image)
