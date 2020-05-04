# ValidatedDC

[![Build Status](https://travis-ci.com/EvgeniyBurdin/validated_dc.svg?branch=master)](https://travis-ci.com/EvgeniyBurdin/validated_dc) [![Coverage Status](https://coveralls.io/repos/github/EvgeniyBurdin/validated_dc/badge.svg?branch=master)](https://coveralls.io/github/EvgeniyBurdin/validated_dc?branch=master)

Dataclass with data validation. Checks the value of its fields by their annotations.

## Capabilities

`ValidatedDC` is a regular Python dataclass.

1. Support for standard types and custom Python classes.
2. Support for some aliases from the `typing` module, namely: `Any`, `List`, `Literal`, `Optional`, `Union`. These aliases can be embedded in each other.
3. When initializing an instance of a class, you can use the value of the field `dict` instead of the `ValidatedDC` instance specified in the field annotation (useful, for example, when retrieving data via api).
4. Data validation occurs immediately after an instance is created, and can also be run by the `is_valid()` method at any time.
5. The `get_errors()` method will show the full traceback of errors in the fields, including errors of nested classes.

See detailed in the `examples` folder.

## Installation

```bash
pip install validated-dc
```

## Simple example

```python
from validated_dc import ValidatedDC
from dataclasses import dataclass

from typing import List, Union


@dataclass
class Foo(ValidatedDC):
    foo: int


@dataclass
class Bar(ValidatedDC):
    bar: Union[Foo, List[Foo]]


foo = {'foo': 1}
instance = Bar(bar=foo)
print(instance.get_errors())  # None
print(instance)               # Bar(bar=Foo(foo=1))

list_foo = [{'foo': 1}, {'foo': 2}]
instance = Bar(bar=list_foo)
print(instance.get_errors())  # None
print(instance)               # Bar(bar=[Foo(foo=1), Foo(foo=2)])

instance.bar.append({'foo': '3'})
print(instance.is_valid())    # False
print(instance.get_errors())
# {'bar': [InstanceValidationError(value_repr='[Foo(foo=1), Foo(foo=2),
# {...]', value_type=<class 'list'>, annotation=<class '__main__.Foo'>,
# exception=None, errors=None), InstanceValidationError(value_repr=
# "{'foo': '3'}", value_type=<class 'dict'>, annotation=<class
# '__main__.Foo'>, exception=None, errors={'foo': [BasicValidationError
# (value_repr='3', value_type=<class 'str'>, annotation=<class 'int'>,
# exception=None)]}), ListValidationError(value_repr="{'foo': '3'}",
# value_type=<class 'dict'>, annotation=<class '__main__.Foo'>,
# exception=None, item_index=2)]}

print(instance)  # Bar(bar=[Foo(foo=1), Foo(foo=2), {'foo': '3'}])

instance.bar[2]['foo'] = 3
print(instance)  # Bar(bar=[Foo(foo=1), Foo(foo=2), {'foo': 3}])
print(instance.is_valid())    # True
print(instance.get_errors())  # None
print(instance)  # Bar(bar=[Foo(foo=1), Foo(foo=2), Foo(foo=3)]

instance.bar[2].foo = '3'
print(instance)  # Bar(bar=[Foo(foo=1), Foo(foo=2), Foo(foo='3')])
print(instance.is_valid())  # False
print(instance.get_errors())
# {'bar': [InstanceValidationError(value_repr='[Foo(foo=1), Foo(foo=2),
# F...]', value_type=<class 'list'>, annotation=<class '__main__.Foo'>,
# exception=None, errors=None), InstanceValidationError(value_repr=
# "{'foo': '3'}", value_type=<class 'dict'>, annotation=<class
# '__main__.Foo'>, exception=None, errors={'foo': [BasicValidationError
# (value_repr='3', value_type=<class 'str'>, annotation=<class 'int'>,
# exception=None)]}), ListValidationError(value_repr="Foo(foo='3')",
# value_type=<class '__main__.Foo'>, annotation=<class '__main__.Foo'>,
# exception=None, item_index=2)]}
```
