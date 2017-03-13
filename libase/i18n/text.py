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
    AttrValuePairDict,
    PropertyDict,
    ListedPropertyDict,
)


class TextBase(object):

    LANGS = {
        'zh_cn',
        'en_us',
    }

    PROPERTIES = LANGS

    ALIASES = {
        'zh': 'zh_cn',
        'en': 'en_us',
    }

    DEFAULT_LANG = 'zh'

    @classmethod
    def derive(cls, langs=None, mapping=None):
        if langs is None:
            langs = ()
        if mapping is None:
            mapping = {}

        class Text(cls):
            LANGS = cls.LANGS + set(langs)

            ALIASES = combine_dicts(cls.ALIASES, mapping)

            locals().update(PropertyDict.create_properties(names=LANGS))
            alias_dict_items(locals(), ALIASES)

        return Text

    def __init__(self, lang=None, default_lang=DEFAULT_LANG, encoding='utf8'):

        self.default_lang = default_lang or self.DEFAULT_LANG
        self.lang = lang or self.default_lang
        self.encoding = encoding

    @property
    def text(self):
        text = getattr(self, self.lang, None)
        if text is not None:
            return text
        return getattr(self, self.default_lang)

    @text.setter
    def text(self, value):
        setattr(self, self.lang, value)

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


class Text(TextBase, PropertyDict):

    locals().update(PropertyDict.create_properties(names=TextBase.LANGS))
    alias_dict_items(locals(), TextBase.ALIASES)

    def __init__(self, mapping=None, _lang=None, _default_lang=None,
            _encoding='utf8', **kwargs):

        args = () if mapping is None else (mapping,)

        TextBase.__init__(
            self,
            lang=_lang,
            default_lang=_default_lang,
            encoding=_encoding,
        )

        PropertyDict.__init__(self, *args, **kwargs)


class ListedText(TextBase, ListedPropertyDict):

    locals().update(ListedPropertyDict.create_properties(attrs=TextBase.LANGS))
    alias_dict_items(locals(), TextBase.ALIASES)

    def __init__(self, iterator=None, _lang=None, _default_lang=None,
            _encoding='utf8', **kwargs):

        TextBase.__init__(
            self,
            lang=_lang,
            default_lang=_default_lang,
            encoding=_encoding,
        )

        items = []

        for item in iterator or ():
            if isinstance(item, (tuple, list)):
                attr, value = item
                items.append(AttrValuePairDict(attr=attr, value=value))
            elif isinstance(item, AttrValuePairDict):
                items.append(item)
            elif isinstance(item, dict):
                items.append(AttrValuePairDict(item))

        ListedPropertyDict.__init__(self, items)

        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)
