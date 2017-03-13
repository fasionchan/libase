#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   schema.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

from ordereddict import (
    OrderedDict,
)

from libase.util.data import NULL as DATA_NULL

from libase.util.data import (
    PropertyDict,
)

no_such_data = DATA_NULL()


def inverse_result(result):

    matched = result[0]
    others = result[1:]

    return (not matched,) + others


class MatchResult(PropertyDict):

    PROPERTIES = [
        'matched',
        'value',
        'original',
        'schema',
    ]

    locals().update(PropertyDict.create_properties(PROPERTIES))

    def __bool__(self):
        return bool(self.matched)

    def __nonzero__(self):
        return self.matched

    def inverse(self):
        self.matched = not self.matched
        return self

    def update(self, **kvs):
        for attr, value in kvs.iteritems():
            setattr(self, attr, value)
        return self

class Schema(object):

    @staticmethod
    def ensure_func(schema, parent, key, value=no_such_data):
        return schema.ensure(
            parent=parent,
            key=key,
            value=value,
        )

    @staticmethod
    def inverse_ensure_func(schema, parent, key, value=no_such_data):
        return inverse_result(
            schema.ensure(
                parent=parent,
                key=key,
                value=value,
                )
            )

    @staticmethod
    def match_func(schema, parent, key, value=no_such_data):
        return schema.match(
            parent=parent,
            key=key,
            value=value,
        )

    @staticmethod
    def create_filler(_callable):
        def filler(root, parent, key):
            return _callable
        return filler

    @staticmethod
    def parse_config(config):
        options = {}
        while isinstance(config, tuple):
            if len(config) == 1:
                config, = config
            else:
                config, _options = config
                _options.update(options)
                options = _options
        return config, options

    subschemas = {}

    @classmethod
    def register(cls, schema_cls):
        cls.subschemas[schema_cls.name] = schema_cls
        return schema_cls

    @classmethod
    def new(cls, *args):
        if len(args) == 1:
            config, = args
            options = {}
            if isinstance(config, tuple):
                config, options = config
        else:
            config, options = args

        config, options = cls.parse_config(args)

        # 类型决定
        if isinstance(config, type):
            return Type(types=(config,), **options)

        # 列表
        if isinstance(config, list):
            if len(config):
                schema = cls.new(config[0])
            else:
                schema = GoodSchema()
            return List(schema=schema, **options)

        if isinstance(config, dict):
            return Doc(schemas=config, **options)

        return Value(values=(config,), **options)


    BASE_SCHEMA_FIELDS = [
        'required',
        'filler',
        'nullable',
        'null_filler',
        'validator',
        'formater',
        'schemaless',
    ]

    def __init__(self, required=True, filler=no_such_data,
            nullable=True, null_filler=no_such_data,
            validator=None, formater=None,
            schemaless=False, path=()):

        # 是否必要字段(是否可缺)
        self.required = required
        # 默认填充字段
        self.filler = filler

        # 是否可以为空
        self.nullable = nullable
        # 空填充字段
        self.null_filler = null_filler

        self.validator = validator
        self.formater = formater

        # 无模式
        self.schemaless = schemaless

        # 路径
        self.path = path

    def kwargs(self):
        kwargs = OrderedDict()

        for field in self.BASE_SCHEMA_FIELDS:
            value = getattr(self, field)
            if value is not no_such_data:
                kwargs[field] = value

        kwargs['path'] = '.'.join(self.path)

        return kwargs

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            ', '.join([
                '%s=%s' % (key, repr(value))
                for key, value in self.kwargs().iteritems()
            ]),
        )

    def __eq__(self, other):
        if not isinstance(other, Schema):
            return False

        for attr in self.BASE_SCHEMA_FIELDS:
            if getattr(self, attr) != getattr(other, attr):
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def inverse(self):
        inverse = getattr(self, '_inverse', None)
        if inverse is None:
            self._inverse = inverse = Inverse(schema=self)
        return inverse

    def match(self, parent, key, root=None, value=no_such_data):

        '''
        是否符合模式
        '''

        original = value

        if self.required:
            if value is no_such_data:
                if self.filler is no_such_data:
                    return MatchResult(
                        matched=False,
                        value=value,
                        original=original,
                        schema=self,
                    )

                if callable(self.filler):
                    value = self.filler(root, parent, key)
                else:
                    value = self.filler

                # 填充值
                parent[key] = value

        if not self.nullable and value is None:
            if self.null_filler is no_such_data:
                return MatchResult(
                    matched=False,
                    value=value,
                    original=original,
                    schema=self,
                )

            if callable(self.null_filler):
                value = self.null_filler(root, parent, key)
            else:
                value = self.null_filler

        matched = self.nullable or value is not None

        return MatchResult(
            matched=matched,
            value=value,
            original=original,
            schema=self,
        )

    def ensure(self, parent, key, root=None, value=no_such_data):

        if root is None:
            root = parent

        if value is no_such_data:
            value = parent.get(key, no_such_data)

        if self.schemaless:
            return MatchResult(
                matched=True,
                value=value,
                original=value,
                schema=self,
            )

        return self.match(
            parent=parent,
            key=key,
            value=value,
        )


class Inverse(Schema):

    def __init__(self, schema, **kwargs):
        super(Inverse, self).__init__(**kwargs)

        self.schema = schema

    def match(self, parent, key, value=no_such_data):
        return self.schema.match(
            parent=parent,
            key=key,
            value=value,
        ).inverse()


class GoodSchema(Schema):

    def __eq__(self, other):
        return isinstance(other, GoodSchema)

    def match(self, parent, key, root=None, value=no_such_data):
        return MatchResult(
            matched=True,
            value=value,
            original=value,
            schema=self,
        )

    def ensure(self, parent, key, value=no_such_data):
        return MatchResult(
            matched=True,
            value=value,
            original=value,
            schema=self,
        )


class BadSchema(Schema):

    def __eq__(self, other):
        return isinstance(other, BadSchema)

    def match(self, parent, key, root=None, value=no_such_data):
        return MatchResult(
            matched=False,
            value=value,
            original=value,
            schema=self,
        )

    def ensure(self, parent, key, value=no_such_data):
        return MatchResult(
            matched=False,
            value=value,
            original=value,
            schema=self,
        )


@Schema.register
class Type(Schema):

    '''
    类型
    '''

    name = 'type'

    TYPE_SCHEMA_FIELDS = [
        'types',
    ]

    def __init__(self, _type=None, types=(), **kwargs):
        if _type is not None:
            types = (_type,) + tuple(types)

        super(Type, self).__init__(**kwargs)

        self.types = types

    def __eq__(self, other):
        for _type in self.types:
            if _type not in other.types:
                return False

        return super(Type, self).__eq__(other)

    def kwargs(self):
        kwargs = OrderedDict()

        for field in self.TYPE_SCHEMA_FIELDS:
            value = getattr(self, field)
            kwargs[field] = value

        kwargs.update(super(Type, self).kwargs())

        return kwargs

    def match(self, parent, key, value=no_such_data):

        '''
        (检查)是否符合模式
        '''

        matched = super(Type, self).match(
            parent=parent,
            key=key,
            value=value,
        )
        if not matched:
            return matched

        value = matched.value

        if value is None:
            return matched

        type_matched = isinstance(value, self.types)

        return matched.update(
            matched=type_matched,
            schema=self,
        )


@Schema.register
class Value(Schema):

    '''
    (数)值
    '''

    name = 'value'

    def __init__(self, value=None, values=(), **kwargs):
        if value is not None:
            values = (value,) + values

        super(Value, self).__init__(**kwargs)

        self.values = values

    def __eq__(self, other):
        for value in self.values:
            if value not in other.values:
                return False
        return super(Value, self).__eq__(other)

    def match(self, parent, key, value=no_such_data):

        '''
        (检查)是否符合模式
        '''

        matched = super(Value, self).match(
            parent=parent,
            key=key,
            value=value,
        )
        if not matched:
            return matched

        if value is None:
            return matched

        value_matched = value in self.values

        return matched.update(
            matched=value_matched,
            schema=self,
        )


@Schema.register
class IsValue(Schema):

    '''
    确值
    '''

    name = 'is_value'

    def __init__(self, value, **kwargs):
        super(IsValue, self).__init__(**kwargs)

        self.value = value

    def match(self, parent, key, value=no_such_data):

        '''
        (检查)是否符合模式
        '''

        matched = super(IsValue, self).match(
            parent=parent,
            key=key,
            value=value,
        )
        if not matched:
            return matched

        is_matched = value is self.value

        return matched.update(
            matched=is_matched,
            schema=self,
        )


@Schema.register
class NONE(IsValue):

    '''
    空
    '''

    name = 'none'

    def __init__(self, **kwargs):
        super(NONE, self).__init__(value=None, **kwargs)


@Schema.register
class TRUE(IsValue):

    '''
    真
    '''

    name = 'true'

    def __init__(self, **kwargs):
        super(TRUE, self).__init__(value=True, **kwargs)


@Schema.register
class FALSE(IsValue):

    '''
    假
    '''

    name = 'false'

    def __init__(self, **kwargs):
        super(FALSE, self).__init__(value=False, **kwargs)


@Schema.register
class List(Schema):

    '''
    列表
    '''

    name = 'list'

    LIST_SCHEMA_FIELDS = [
        'schema',
        'size',
        'size_lower',
        'size_upper',
    ]

    def __init__(self, schema=None, size=None, size_lower=None, size_upper=None,
            **kwargs):

        super(List, self).__init__(**kwargs)

        self.schema = schema if isinstance(schema, Schema) else Schema.new(schema)
        self.size = size
        self.size_lower = size_lower
        self.size_upper = size_upper

    def kwargs(self):
        kwargs = OrderedDict([
            (attr, getattr(self, attr))
            for attr in self.LIST_SCHEMA_FIELDS
        ])
        kwargs.update(super(List, self).kwargs())
        return kwargs

    def __eq__(self, other):
        for attr in self.LIST_SCHEMA_FIELDS:
            if getattr(self, attr) != getattr(other, attr):
                return False

        return super(List, self).__eq__(other)

    def match(self, parent, key, value=no_such_data):
        matched= super(List, self).match(
            parent=parent,
            key=key,
            value=value,
        )
        if not matched:
            return matched

        value = matched.value
        if value is None:
            return matched

        if not isinstance(value, (list, tuple)):
            return matched.update(
                matched=False,
                schema=self,
            )

        if self.size is not None:
            size_matched = len(value) == self.size
            if not size_matched:
                return matched.update(
                    matched=size_matched,
                    schema=self,
                )

        if self.size_lower is not None:
            size_matched = len(value) >= self.size_lower
            if not size_matched:
                return matched.update(
                    matched=size_matched,
                    schema=self,
                )

        if self.size_upper is not None:
            size_matched = len(value) <= self.size_upper
            if not size_matched:
                return matched.update(
                    matched=size_matched,
                    schema=self,
                )

        for index, item in enumerate(value):
            _matched = self.schema.ensure(
                parent=value,
                key=index,
                value=item,
            )
            if not _matched:
                return _matched

        return matched


@Schema.register
class Doc(Schema):

    '''
    文档
    '''

    name = 'doc'

    DOC_SCHEMA_FIELDS = [
        'schemas',
        'more',
    ]

    @staticmethod
    def extract_config(config):
        extra = {}
        for key in config.keys():
            if key.startswith('__') and key.endswith('__'):
                value = config.pop(key)
                key = key[2:-2]
                extra[key] = value
        return extra

    def __init__(self, schemas, more=False, **kwargs):

        extra = self.extract_config(config=schemas)
        _more = extra.pop('more', None)
        if _more is not None:
            more = _more
        extra.update(kwargs)

        super(Doc, self).__init__(**extra)

        self.schemas = {}
        for field, config in schemas.iteritems():
            if isinstance(config, Schema):
                schema = config
            else:
                config, options = self.parse_config(config)
                options['path'] = self.path + (field,)
                schema = Schema.new(config, options)
            self.schemas[field] = schema

        self.more = more

    def __eq__(self, other):
        if not isinstance(other, Doc):
            return False

        for field in self.DOC_SCHEMA_FIELDS:
            if getattr(self, field) != getattr(other, field):
                return False

        return super(Doc, self).__eq__(other)

    def kwargs(self):
        kwargs = OrderedDict([
            (field, getattr(self, field))
            for field in self.DOC_SCHEMA_FIELDS
        ])
        kwargs.update(super(Doc, self).kwargs())
        return kwargs

    def match(self, parent, key, value=no_such_data):
        matched= super(Doc, self).match(
            parent=parent,
            key=key,
            value=value,
        )
        if not matched:
            return matched

        if matched.value is None:
            return matched

        for field, schema in self.schemas.iteritems():
            _matched = schema.ensure(parent=value, key=field)
            if not _matched:
                return _matched

        if not self.more:
            for field in value:
                if field not in self.schemas:
                    return matched.update(
                        matched=False,
                        schema=self,
                    )

        return matched.update(
            schema=self,
        )


class IS(Schema):

    '''
    是
    '''


@Schema.register
class OR(Schema):

    '''
    或
    '''

    name = 'or'

    judge_func = staticmethod(Schema.ensure_func)

    def __init__(self, *schemas, **kwargs):
        super(OR, self).__init__(**kwargs)

        schemas = [
            schema if isinstance(schema, Schema) else Schema.new(schema)
            for schema in schemas
        ]
        self.schemas = schemas

    def match(self, parent, key, value=no_such_data):
        matched= super(OR, self).match(
            parent=parent,
            key=key,
            value=value,
        )
        if not matched:
            return matched

        for schema in self.schemas:
            _matched = self.judge_func(
                schema=schema,
                parent=parent,
                key=key,
                value=value,
            )
            if _matched:
                return _matched

        return matched.update(
            matched=False,
            schema=self,
        )


class NOT(Schema):

    '''
    非
    '''

    judge_func = staticmethod(Schema.inverse_ensure_func)
