import copy
from dataclasses import dataclass

from validated_dc import BasicValidation


class СustomСlass:

    foo = 'foo'

    def method(self):
        pass


@dataclass
class Foo(BasicValidation):
    i: int
    s: str
    l: list
    # ... You can use all other standard python classes.
    cc: СustomСlass


correct_input = {
    'i': 1,
    's': '2',
    'l': [3, '4'],
    'cc': СustomСlass()
}


def test_basic_validation_valid():

    instance = Foo(**correct_input)

    assert instance.get_errors() is None
    assert instance.is_valid()


def test_basic_validation_not_valid():

    nocorrect_input = copy.copy(correct_input)
    nocorrect_input['s'] = 2
    nocorrect_input['cc'] = 5

    instance = Foo(**nocorrect_input)

    # Есть ошибки в данных
    assert instance.get_errors()
    assert not instance.is_valid()

    fields_errors = set([key for key in instance.get_errors().keys()])
    # Данные в полях s и cc имеют ошибки
    assert fields_errors == set(['s', 'cc'])


def test__post_init__():
    """
        Тест запуска валидации после создания экземпляра
        (в методе self.__post_init__())
    """
    @dataclass
    class FakeBasicValidation(BasicValidation):
        """
            Подменим метод старта валидаци
        """
        def _run_validation(self):
            self._validation__started = True

    instance = FakeBasicValidation()
    assert instance._validation__started


def test_get_errors():

    instance = Foo(**correct_input)
    assert instance.get_errors() is None

    nocorrect_input = copy.copy(correct_input)
    nocorrect_input['s'] = 2
    nocorrect_input['cc'] = 5
    instance = Foo(**nocorrect_input)
    assert instance._errors == instance.get_errors()


def test_is_valid():

    instance = Foo(**correct_input)
    assert instance.is_valid()

    nocorrect_input = copy.copy(correct_input)
    nocorrect_input['s'] = 2
    nocorrect_input['cc'] = 5
    instance = Foo(**nocorrect_input)
    assert not instance.is_valid()


def test_init_validation():

    # Возьмем произвольный экземпляр
    instance = Foo(**correct_input)

    instance._init_validation()
    assert instance._errors == {}


def test_is_instance_true():

    # Возьмем произвольный экземпляр
    instance = Foo(**correct_input)

    custom_class_instance = СustomСlass()

    values = (
        None, True, 0.1, 1, complex(3, 4), set([5, ]), frozenset('7'),
        (7, 8), [9, ], {11: 12},
        custom_class_instance, custom_class_instance.method,
        instance, instance.is_valid
    )

    data = {type(value): value for value in values}

    for type_, value in data.items():
        assert instance._is_instance(value, type_)


def test_is_instance_false():

    # Возьмем произвольный валидный экземпляр
    instance = Foo(**correct_input)

    custom_class_instance = СustomСlass()

    values = (
        None, True, 0.1, 1, '2', complex(3, 4), set([5, ]), frozenset('7'),
        (7, 8), [9, ], {11: 12},
        custom_class_instance, custom_class_instance.method
    )

    data = {type(value): value for value in values}
    instance._field_errors = []
    for type_, value in data.items():
        value = 1 if value == '2' else '2'  # Обеспечим невалидность
        assert not instance._is_instance(value, type_)

    assert len(instance._field_errors) == len(values)
