# ValidatedDC

[![PyPI version](https://badge.fury.io/py/validated-dc.svg)](https://badge.fury.io/py/validated-dc) [![Build Status](https://travis-ci.com/EvgeniyBurdin/validated_dc.svg?branch=master)](https://travis-ci.com/EvgeniyBurdin/validated_dc) [![Coverage Status](https://coveralls.io/repos/github/EvgeniyBurdin/validated_dc/badge.svg?branch=master)](https://coveralls.io/github/EvgeniyBurdin/validated_dc?branch=master) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/EvgeniyBurdin/validated_dc.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/EvgeniyBurdin/validated_dc/context:python) [![Total alerts](https://img.shields.io/lgtm/alerts/g/EvgeniyBurdin/validated_dc.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/EvgeniyBurdin/validated_dc/alerts/) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/validated-dc)

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

## python 3.7 support

Support for `typing.Literal` has appeared in *python 3.8*. But you can use `ValidatedDC` in *python 3.7*.
To do this, just copy the file `validated_dc.py` into your project (without installing the package) and change the import in it so:

```python
...
from typing import Any, Callable, List, Optional, Union
from typing_extensions import Literal
...
```

## Quick example

```python
from dataclasses import dataclass
from typing import List, Union

from validated_dc import ValidatedDC


# Some combinations of List and Union

@dataclass
class Foo(ValidatedDC):
    value: Union[int, List[int]]


@dataclass
class Bar(ValidatedDC):
    foo: Union[Foo, List[Foo]]


# --- Valid input ---

foo = {'value': 1}
instance = Bar(foo=foo)
assert instance.get_errors() is None
assert instance == Bar(foo=Foo(value=1))

foo = {'value': [1, 2]}
instance = Bar(foo=foo)
assert instance.get_errors() is None
assert instance == Bar(foo=Foo(value=[1, 2]))

foo = [{'value': 1}, {'value': 2}]
instance = Bar(foo=foo)
assert instance.get_errors() is None
assert instance == Bar(foo=[Foo(value=1), Foo(value=2)])

foo = [{'value': [1, 2]}, {'value': [3, 4]}]
instance = Bar(foo=foo)
assert instance.get_errors() is None
assert instance == Bar(foo=[Foo(value=[1, 2]), Foo(value=[3, 4])])


# --- Invalid input ---

foo = {'value': 'S'}
instance = Bar(foo=foo)
assert instance.get_errors()
assert instance == Bar(foo={'value': 'S'})
# fix
instance.foo['value'] = 1
assert instance.is_valid()
assert instance.get_errors() is None
assert instance == Bar(foo=Foo(value=1))

foo = [{'value': [1, 2]}, {'value': ['S', 4]}]
instance = Bar(foo=foo)
assert instance.get_errors()
assert instance == Bar(foo=[{'value': [1, 2]}, {'value': ['S', 4]}])
# fix
instance.foo[1]['value'][0] = 3
assert instance.is_valid()
assert instance.get_errors() is None
assert instance == Bar(foo=[Foo(value=[1, 2]), Foo(value=[3, 4])])


# --- get_errors() ---

foo = {'value': 'S'}
instance = Bar(foo=foo)
print(instance.get_errors())
# {
#   'foo': [
#       # An unsuccessful attempt to use the dictionary to create a Foo instance
#       InstanceValidationError(
#           value_repr="{'value': 'S'}",
#           value_type=<class 'dict'>,
#           annotation=<class '__main__.Foo'>,
#           exception=None,
#           errors={
#               'value': [
#                   BasicValidationError(  # because the str isn't an int
#                       value_repr='S', value_type=<class 'str'>,
#                       annotation=<class 'int'>, exception=None
#                   ),
#                   BasicValidationError(  # and the str is not a list of int
#                       value_repr='S', value_type=<class 'str'>,
#                       annotation=typing.List[int], exception=None
#                   )
#               ]
#           }
#       ),
#       BasicValidationError(  # the dict is not a list of Foo
#           value_repr="{'value': 'S'}",
#           value_type=<class 'dict'>,
#           annotation=typing.List[__main__.Foo],
#           exception=None
#       )
#   ]
# }

```
