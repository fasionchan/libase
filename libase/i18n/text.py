#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   text.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''


from libase.util.data import (
    alias_dict_items,
    combine_dicts,
    get_dict_property,
    get_dict_properties,
)


class Text(dict):

    LANGS = {
        'zh_cn',
        'en_us',
    }

    ALIASES = {
        'zh': 'zh_cn',
        'en': 'en_us',
    }

    DEFAULT_LANG = 'zh'

    locals().update(get_dict_properties(names=LANGS))
    alias_dict_items(locals(), ALIASES)

    @classmethod
    def derive(cls, langs=None, mapping=None):
        if langs is None:
            langs = ()
        if mapping is None:
            mapping = {}

        class Text(cls):
            LANGS = cls.LANGS + set(langs)

            ALIASES = combine_dicts(cls.ALIASES, mapping)

            locals().update(get_dict_properties(names=LANGS))
            alias_dict_items(locals(), ALIASES)

        return Text

    def __init__(self, mapping=None, _lang=None, _default_lang=None,
            _encoding='utf8', **kwargs):

        args = () if mapping is None else (mapping,)
        super(Text, self).__init__(*args, **kwargs)

        self.default_lang = _default_lang or self.DEFAULT_LANG
        self.lang = _lang or self.default_lang

        self.encoding = _encoding

    @property
    def text(self):
        text = getattr(self, self.lang, None)
        if text is not None:
            return text
        return getattr(self, self.default_lang)

    def __str__(self):
        text = self.text
        if isinstance(text, unicode):
            return text.encode(self.encoding)
        return text

    def __unicode__(self):
        text = self.text
        if isinstance(text, unicode):
            return text
        return text.decode(self.encoding)
