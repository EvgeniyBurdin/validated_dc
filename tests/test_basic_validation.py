import copy
from dataclasses import dataclass, fields

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
        Тест инициализации свойст необходимых для валидации.
        (в данном случае только одно свойство - self._errors)
    """
    # Возьмем произвольный экземпляр
    instance = Foo(**correct_input)

    instance._errors == {1: 1}  # Присвоим любое непустое значение

    instance._init_validation()
    assert instance._errors == {}


def test_init_field_validation():
    """
        Тест инициализации свойст необходимых при валидации каждого поля.
    """
    # Возьмем корректный экземпляр
    instance = Foo(**correct_input)

    # Возьмем первое поле у экземпляра
    field = fields(instance)[0]

    # Возьмем первые имя ключа и значение из словаря исходных данных
    input_name, input_value = list(correct_input.items())[0]

    # Вызовем метот инициализации свойств для валидации этого поля
    instance._init_field_validation(field)

    # Проверим свойства необходимые для начала валидации поля:

    # ... список ошибок должен быть пустой
    assert instance._field_errors == []
    # ... должно быть сохранено имя поля
    assert instance._field_name == input_name
    # ... должно быть сохранено значение поля
    assert instance._field_value == input_value
    # ... должна быть сохранена аннотация поля
    assert instance._field_annotation == type(input_value)


def test_is_instance_true():
    """
        Тест успешной работы метода self.is_instance() (возвращает True)
    """
    # Возьмем произвольный экземпляр
    instance = Foo(**correct_input)

    custom_class_instance = СustomСlass()

    # Кортеж из значений всех (вроде :) ) стандартных типов Python и пары
    # пользовательских классов
    values = (
        None, True, 0.1, 1, complex(3, 4), set([5, ]), frozenset('7'),
        (7, 8), [9, ], {11: 12},
        custom_class_instance, custom_class_instance.method, instance
    )

    data = {type(value): value for value in values}

    for type_, value in data.items():
        # Все проверки должны вернуть True
        assert instance._is_instance(value, type_)


def test_is_instance_false():
    """
        Тест НЕ успешной работы метода self.is_instance() (возвращает False)
    """
    # Возьмем валидный экземпляр
    instance = Foo(**correct_input)

    custom_class_instance = СustomСlass()

    # Кортеж из значений всех (вроде :) ) стандартных типов Python и пары
    # пользовательских классов
    values = (
        None, True, 0.1, 1, '2', complex(3, 4), set([5, ]), frozenset('7'),
        (7, 8), [9, ], {11: 12},
        custom_class_instance, custom_class_instance.method, instance,
    )

    data = {type(value): value for value in values}

    # Подготовим гарантированно пустой список для ошибок
    instance._field_errors = []

    for type_, value in data.items():
        value = 1 if value == '2' else '2'  # Обеспечим невалидность
        # Все проверки должны вернуть False
        assert not instance._is_instance(value, type_)

    # Ошибки были при проверке каждой items из data,
    # таким образом - длины списков должны быть равны
    assert len(instance._field_errors) == len(values)


def test_is_instance_false_and_set_exception():
    """
        Тест НЕ успешной работы метода self.is_instance() (возвращает False)
        в случае возникновения исключения при передаче в метод некорректных
        аргументов.

        Если передать в метод некорректные аргументы, то возниктнет исключение,
        которое будет "погашено", но само исключение сохранится в ошибке поля.
    """
    # Возьмем валидный экземпляр
    instance = Foo(**correct_input)

    # Подготовим гарантированно пустой список для ошибок
    instance._field_errors = []

    # Вызовем метод с аргументами, которые поднимут исключение
    result = instance._is_instance(1, 1)
    # Но метод его должен "погасить" и вернуть False
    assert not result

    # а в instance._field_errors[0].exception должен быть экземпляр исключения
    assert isinstance(instance._field_errors[0].exception, Exception)


def test_save_current_field_errors():
    """
        Тест сохранения списка ошибок поля в словаре ошибок всего экземпляра.
    """
    # Возьмем валидный экземпляр
    instance = Foo(**correct_input)

    # Его словарь ошибок должен быть пустой
    assert instance._errors == {}

    # Допустим, сейчас проверяли поле i, и его список ошибок не пуст
    instance._field_name = 'i'
    instance._field_errors = ['Просто строка для непустого списка', ]

    # Вызовем метод сохранения ошибки текущего поля
    instance._save_current_field_errors()

    # Словарь ошибок должен иметь ключ с именем поля и
    # значением равным списку ошибок
    assert instance._errors[instance._field_name] == instance._field_errors
