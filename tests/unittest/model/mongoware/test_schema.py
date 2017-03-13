#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   test_schema.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import pytest

from libase.model.mongoware.schema import (
    Schema,

    Inverse,
    GoodSchema,
    BadSchema,

    Type,
    Value,
    List,
    Doc,

    NONE,
    TRUE,
    FALSE,

    OR,

    no_such_data,
)
from libase.util.data import (
    NULL,
)

null = NULL()

def case(schema, value, expected, expected_value=null, expected_original=null):
    if expected_value is null:
        expected_value = value
    if expected_original is null:
        expected_original = value
    return schema, value, expected, expected_value, expected_original


class TestSchema(object):

    schema_test_data = [
        # 基本属性

        # 特殊模式
        case(GoodSchema(), no_such_data, True, no_such_data, no_such_data),
        case(BadSchema(), no_such_data, False, no_such_data, no_such_data),

        # 反模式
        case(Inverse(GoodSchema()), no_such_data, False, no_such_data, no_such_data),
        case(Inverse(BadSchema()), no_such_data, True, no_such_data, no_such_data),

        # 无模式
        case(Schema(required=True, schemaless=True), no_such_data, True),
        case(Schema(required=True, filler=lambda *args, **kwargs: 1, schemaless=True), no_such_data, True, no_such_data, no_such_data),
        case(Schema(nullable=False, schemaless=True), no_such_data, True),
        case(Schema(nullable=False, null_filler=lambda *args, **kwargs: 1, schemaless=True), no_such_data, True, no_such_data, no_such_data),

        # 必要性
        case(Schema(required=True), 1, True),
        case(Schema(required=False), 1, True),
        case(Schema(required=True), no_such_data, False),
        case(Schema(required=False), no_such_data, True),

        # 默认填充
        case(Schema(required=True, filler=lambda *args, **kwargs: 1), no_such_data, True, 1, no_such_data),
        case(Schema(required=False, filler=lambda *args, **kwargs: 1), no_such_data, True),

        # 空值
        case(Schema(nullable=True), 1, True),
        case(Schema(nullable=False), 1, True),
        case(Schema(nullable=True), None, True),
        case(Schema(nullable=False), None, False),

        # 空值填充
        case(Schema(nullable=True, null_filler=lambda *args, **kwargs: 1), None, True),
        case(Schema(nullable=False, null_filler=lambda *args, **kwargs: 1), None, True, 1, None),
        case(Schema(nullable=False, null_filler=lambda *args, **kwargs: None), None, False, None, None),

        # 类型
        case(Type(_type=int), 1, True),
        case(Type(_type=int), '', False),

        case(Type(types=(int,)), 1, True),
        case(Type(types=(int,)), '', False),

        case(Type(_type=float, types=(int,)), 1, True),
        case(Type(_type=float, types=(int,)), 1., True),
        case(Type(_type=float, types=(int,)), '', False),

        # (数)值
        case(Value(1), 1, True),
        case(Value(1), 2, False),
        case(Value(value=1), 1, True),
        case(Value(value=1), 2, False),
        case(Value(values=(1,)), 1, True),
        case(Value(values=(1,)), 2, False),
        case(Value(values=(1,2)), 2, True),

        # 空
        case(NONE(), 0, False),
        case(NONE(), False, False),
        case(NONE(), '', False),
        case(NONE(), None, True),

        # 真
        case(TRUE(), 1, False),
        case(TRUE(), True, True),

        # 假
        case(FALSE(), 0, False),
        case(FALSE(), None, False),
        case(FALSE(), False, True),

        # 列表
        case(List(GoodSchema()), [], True, [], []),
        case(List(GoodSchema()), 1, False, 1, 1),

        case(List(GoodSchema(), size=3), range(3), True, range(3), range(3)),
        case(List(GoodSchema(), size=3), range(2), False, range(2), range(2)),

        case(List(GoodSchema(), size_lower=2), range(3), True, range(3), range(3)),
        case(List(GoodSchema(), size_lower=3), range(3), True, range(3), range(3)),
        case(List(GoodSchema(), size_lower=4), range(3), False, range(3), range(3)),
        case(List(GoodSchema(), size=2, size_lower=3), range(3), False, range(3), range(3)),

        case(List(GoodSchema(), size_upper=2), range(3), False, range(3), range(3)),
        case(List(GoodSchema(), size_upper=3), range(3), True, range(3), range(3)),
        case(List(GoodSchema(), size_upper=4), range(3), True, range(3), range(3)),
        case(List(GoodSchema(), size=2, size_upper=4), range(3), False, range(3), range(3)),

        case(List(GoodSchema(), size_lower=2, size_upper=4), range(1), False, range(1), range(1)),
        case(List(GoodSchema(), size_lower=2, size_upper=4), range(2), True, range(2), range(2)),
        case(List(GoodSchema(), size_lower=2, size_upper=4), range(3), True, range(3), range(3)),
        case(List(GoodSchema(), size_lower=2, size_upper=4), range(4), True, range(4), range(4)),
        case(List(GoodSchema(), size_lower=2, size_upper=4), range(5), False, range(5), range(5)),
        case(List(GoodSchema(), size=2, size_lower=2, size_upper=4), range(3), False, range(3), range(3)),

        case(List(Type(int), size=3), range(3), True, range(3), range(3)),
        case(List(Type(int), size=3), [1, 1., 2], False, 1., 1.),

        # 文档
        case(Doc(dict(a=GoodSchema())), dict(a=1), True, dict(a=1), dict(a=1)),
        case(Doc(dict(a=GoodSchema())), dict(a=1, b=2), False, dict(a=1, b=2), dict(a=1, b=2)),
        case(Doc(dict(a=GoodSchema()), more=True), dict(a=1, b=2), True, dict(a=1, b=2), dict(a=1, b=2)),

        case(Doc(dict(a=GoodSchema(), b=GoodSchema())), dict(a=1), True, dict(a=1), dict(a=1)),
        case(Doc(dict(a=GoodSchema(), b=BadSchema())), dict(a=1), False, no_such_data, no_such_data),
        case(Doc(dict(a=GoodSchema(), b=GoodSchema())), dict(a=1, b=2), True, dict(a=1, b=2), dict(a=1, b=2)),
        case(Doc(dict(a=GoodSchema(), b=BadSchema())), dict(a=1, b=2), False, no_such_data, no_such_data),

        # OR
        case(OR(GoodSchema()), 1, True, 1, 1),
        case(OR(GoodSchema(), GoodSchema()), 1, True, 1, 1),
        case(OR(GoodSchema(), BadSchema()), 1, True, 1, 1),
        case(OR(BadSchema(), GoodSchema()), 1, True, 1, 1),
        case(OR(BadSchema(), BadSchema()), 1, False, 1, 1),
        case(OR(BadSchema()), 1, False, 1, 1),
    ]

    @pytest.mark.parametrize('schema,value,expected,expected_value,expected_original', schema_test_data)
    def test_schema(self, schema, value, expected, expected_value,
            expected_original):

        key = 'data'
        data = {} if value is no_such_data else {
            key: value,
        }

        matched = schema.ensure(data, key)

        assert matched.matched == expected

        if expected_value is not null:
            assert matched.value == expected_value

        if expected_original is not null:
            assert matched.original == expected_original

    schema_eq_test_data = [
        (Schema(), Schema(), True),

        (Schema(required=True), Schema(required=True), True),
        (Schema(required=True), Schema(required=False), False),
        (Schema(required=False), Schema(required=True), False),
        (Schema(required=False), Schema(required=False), True),

        (Schema(nullable=True), Schema(nullable=True), True),
        (Schema(nullable=True), Schema(nullable=False), False),
        (Schema(nullable=False), Schema(nullable=True), False),
        (Schema(nullable=False), Schema(nullable=False), True),

        (Schema(schemaless=True), Schema(schemaless=True), True),
        (Schema(schemaless=True), Schema(schemaless=False), False),
        (Schema(schemaless=False), Schema(schemaless=True), False),
        (Schema(schemaless=False), Schema(schemaless=False), True),

        # 类型
        (Schema.new(int), Type(types=(int,)), True),
        (Schema.new(int), Type(types=(float,)), False),

        (Schema.new(int, dict(required=True)), Type(types=(int,), required=True), True),
        (Schema.new(int, dict(required=True)), Type(types=(int,), required=False), False),
        (Schema.new(int, dict(required=False)), Type(types=(int,), required=True), False),
        (Schema.new(int, dict(required=False)), Type(types=(int,), required=False), True),

        # 数值
        (Schema.new(1), Value(values=(1,)), True),
        (Schema.new(1), Value(values=(2,)), False),

        (Schema.new(1, dict(required=True)), Value(values=(1,), required=True), True),
        (Schema.new(1, dict(required=True)), Value(values=(1,), required=False), False),
        (Schema.new(1, dict(required=False)), Value(values=(1,), required=True), False),
        (Schema.new(1, dict(required=False)), Value(values=(1,), required=False), True),

        # 列表
        (Schema.new([]), List(schema=GoodSchema()), True),
        (Schema.new([int]), List(schema=Type(types=(int,))), True),
        (Schema.new([int]), List(schema=Type(types=(float,))), False),

        (Schema.new([int], dict(required=True)), List(schema=Type(types=(int,)), required=True), True),
        (Schema.new([int], dict(required=True)), List(schema=Type(types=(int,)), required=False), False),
        (Schema.new([int], dict(required=False)), List(schema=Type(types=(int,)), required=True), False),
        (Schema.new([int], dict(required=False)), List(schema=Type(types=(int,)), required=False), True),

        (Schema.new([int], dict(size=10)), List(schema=Type(types=(int,)), size=10), True),
        (Schema.new([int], dict(size=10)), List(schema=Type(types=(int,)), size=11), False),

        (Schema.new([int], dict(size_lower=10)), List(schema=Type(types=(int,)), size_lower=10), True),
        (Schema.new([int], dict(size_lower=10)), List(schema=Type(types=(int,)), size_lower=11), False),

        (Schema.new([int], dict(size_upper=10)), List(schema=Type(types=(int,)), size_upper=10), True),
        (Schema.new([int], dict(size_upper=10)), List(schema=Type(types=(int,)), size_upper=11), False),

        # 文档
        (Schema.new(dict()), Doc(schemas=dict()), True),
        (Schema.new(dict(a=int)), Doc(schemas=dict(a=int)), True),
        (Schema.new(dict(a=int)), Doc(schemas=dict(a=float)), False),

        (Schema.new(dict(a=int), dict(required=True)), Doc(schemas=dict(a=int), required=True), True),
        (Schema.new(dict(a=int), dict(required=True)), Doc(schemas=dict(a=int), required=False), False),
        (Schema.new(dict(a=int), dict(required=False)), Doc(schemas=dict(a=int), required=True), False),
        (Schema.new(dict(a=int), dict(required=False)), Doc(schemas=dict(a=int), required=False), True),

        (Schema.new(dict(a=int), dict(more=True)), Doc(schemas=dict(a=int), more=True), True),
        (Schema.new(dict(a=int), dict(more=True)), Doc(schemas=dict(a=int), more=False), False),
        (Schema.new(dict(a=int), dict(more=False)), Doc(schemas=dict(a=int), more=True), False),
        (Schema.new(dict(a=int), dict(more=False)), Doc(schemas=dict(a=int), more=False), True),

    ]
    [

    ]

    @pytest.mark.parametrize('a,b,expected', schema_eq_test_data)
    def test_schema_equivalency(self, a, b, expected):
        if expected:
            assert a == b
        else:
            assert a != b
