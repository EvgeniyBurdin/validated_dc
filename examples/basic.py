from dataclasses import dataclass
from validated_dc import ValidatedDC


def any_function_1():
    pass


def any_function_2():
    pass


class AnyClass:
    pass


@dataclass
class MyData(ValidatedDC):
    int_field: int
    float_field: float
    str_field: str
    list_field: list
    dict_field: dict
    # ...
    function_field: type(any_function_1)
    instance_field: AnyClass


# --- Valid input ---

input_data = {
    'int_field': 1,
    'float_field': 2.0,
    'str_field': '3',
    'list_field': [4, '5'],
    'dict_field': {6: 7},
    'function_field': any_function_1,
    'instance_field': AnyClass(),
}
instance = MyData(**input_data)
assert instance.get_errors() is None

# --- Errorr input ---

input_data['int_field'] = '1'     # Error - str is not int
input_data['function_field'] = 2  # Error - int is not function
instance = MyData(**input_data)
assert instance.get_errors()
print(instance.get_errors())

# fix
instance.int_field = 1
instance.function_field = any_function_2
assert instance.is_valid()
assert instance.get_errors() is None
