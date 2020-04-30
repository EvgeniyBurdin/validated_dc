# ValidatedDC

Dataclass with data validation. Checks the value of its fields by their annotations.

## Capabilities

`ValidatedDC` is a regular Python dataclass, but with the ability to check the validity of the data by which this dataclass was initialized. Also, you can check the data at any time during the life of the instance.

1. Support for standard and custom Python classes.
2. Support for some aliases from the `typing` module, namely: `Any`, `List`, `Literal`, `Optional`, `Union`. These aliases can be embedded in each other.
3. Replacing the `dict` with an instance of the `dataclass` from the field annotation (for example, when receiving data by api). If this behavior is not necessary, then the replacement can be disabled as follows:

    ```python
    from dataclasses import dataclass
    from validated_dc import ValidatedDC

    @dataclass
    class CustomValidatedDC(ValidatedDC):
        def _init_validation(self) -> None:
            super()._init_validation()
            self._replace = False
    ```

4. You can still get the dictionary from the instance by applying `asdict()` to it:

    ```python
    from dataclasses import asdict, dataclass
    from validated_dc import ValidatedDC

    @dataclass
    class Foo(ValidatedDC):
        i: int
        d: str = 'bar'

    @dataclass
    class MyValidatedDC(ValidatedDC):
        foo: Foo

    data = {'i': 1}
    instance = MyValidatedDC(foo=data)
    print(instance.get_errors())  # None
    instance_dict = asdict(instance)
    print(instance_dict)  # {'foo': {'i': 1, 'd': 'bar'}}
    ```

    You get valid data + default values.

See detailed examples in `examples.py`.

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
