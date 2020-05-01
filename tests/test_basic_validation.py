import copy
from dataclasses import dataclass

from validated_dc import BasicValidation


class СustomСlass:
    """
        Пользовательский класс
    """
    foo = 'foo'

    def method(self):
        pass


@dataclass
class Foo(BasicValidation):
    """
        Датакласс с валидацией для использования в тестах
    """
    i: int
    s: str
    l: list
    # ... You can use all other standard python classes.
    cc: СustomСlass

# Корректные данные для создания экземпляра Foo
correct_input = {
    'i': 1,
    's': '2',
    'l': [3, '4'],
    'cc': СustomСlass()
}


def test_basic_validation_valid():
    """
        Тест отсутствия ошибок у валидного класса
    """
    instance = Foo(**correct_input)

    assert instance.get_errors() is None
    assert instance.is_valid()


def test_basic_validation_not_valid():
    """
        Тест наличия ошибок у НЕ валидного класса
    """
    nocorrect_input = copy.copy(correct_input)
    nocorrect_input['s'] = 2
    nocorrect_input['cc'] = 5

    instance = Foo(**nocorrect_input)

    # В полях датакласса есть ошибки
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
            self._validation__started = True  # Установим маркер

    instance = FakeBasicValidation()
    # Проверим наличие маркера
    assert instance._validation__started


def test_get_errors():
    """
       get_errors() должна вернуть None если все поля валидны, или список
       ошибок у полей.
    """
    instance = Foo(**correct_input)
    assert instance.get_errors() is None

    nocorrect_input = copy.copy(correct_input)
    nocorrect_input['s'] = 2
    nocorrect_input['cc'] = 5
    instance = Foo(**nocorrect_input)
    #  Список ошибок хранится в приватном поле instance._errors
    assert instance._errors == instance.get_errors()


def test_is_valid():
    """
        is_valid() должен запустить валидацию и вернуть True если ошибок нет,
        или False если они есть.
    """

    instance = Foo(**correct_input)
    assert instance.is_valid()

    instance.s = 5  # Присвоим полю невалидное значение
    assert not instance.is_valid()


def test_init_validation():
    """
        Тест создания и инициализации свойст необходимых для валидации.
        (в данном случае только одно свойство - self._errors)
    """
    # Возьмем произвольный экземпляр
    instance = Foo(**correct_input)

    instance._init_validation()
    assert instance._errors == {}


def test_is_instance_true():
    """
        Тест успешной работы метода self.is_instance() (возвращает True)
    """
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
        # Все проверки должны вернуть True
        assert instance._is_instance(value, type_)


def test_is_instance_false():
    """
        Тест НЕ успешной работы метода self.is_instance() (возвращает False)
    """
    # Возьмем произвольный валидный экземпляр
    instance = Foo(**correct_input)

    custom_class_instance = СustomСlass()

    values = (
        None, True, 0.1, 1, '2', complex(3, 4), set([5, ]), frozenset('7'),
        (7, 8), [9, ], {11: 12},
        custom_class_instance, custom_class_instance.method
    )

    data = {type(value): value for value in values}

    # Подготовим пустой список для ошибок
    instance._field_errors = []

    for type_, value in data.items():
        value = 1 if value == '2' else '2'  # Обеспечим невалидность
        # Все проверки должны вернуть False
        assert not instance._is_instance(value, type_)

    # Ошибки были при проверке каждой items из data,
    # то есть - длины списков должны быть равны
    assert len(instance._field_errors) == len(values)
