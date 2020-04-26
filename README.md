# ValidatedDC

Dataclass with data validation.
Checks the value of its fields by their annotations.

## Capabilities

1. Support for standard and custom Python classes.
2. Support for some aliases from the `typing` module, namely: `Any`, `List`, `Literal`, `Optional`, `Union`.
3. Replacing the `dict` with an instance of the dataclass.

`ValidatedDC` is a regular Python dataclass, but with the ability to check the validity of the data by which this dataclass was initialized. Also, you can check the data at any time during the life of the instance.

See detailed examples in `examoles.py`

## Simple example

```python
from data_classes import ValidatedDC
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
# [{'field_name': 'bar', 'field_value': [Foo(foo=1), Foo(foo=2), {'foo': '3'}],
# 'field_type': <class '__main__.Foo'>}, {<class '__main__.Foo'>:
# [{'field_name': 'foo', 'field_value': '3', 'field_type': <class 'int'>}]},
# {'field_name': 'bar', 'field_value': {'foo': '3'}, 'field_type':
# <class '__main__.Foo'>}]

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
# [{'field_name': 'bar', 'field_value': [Foo(foo=1), Foo(foo=2), 
# Foo(foo='3')], 'field_type': <class '__main__.Foo'>}, 
# {<class '__main__.Foo'>: [{'field_name': 'foo', 'field_value': '3', 
# 'field_type': <class 'int'>}]}]

```
