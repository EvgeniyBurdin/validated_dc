from dataclasses import dataclass,fields

from validated_dc import InstanceValidation


@dataclass
class Foo(InstanceValidation):
    i: int


@dataclass
class Bar(InstanceValidation):
    foo: Foo


def test_init_validation():
    """
        Тест инициализации свойст для валидации экземпляра.
    """
    # Для валидации экземпляра класса InstanceValidation, дополнительно к
    # свойствам родителя, свойство self._replace инициализируется
    # значением True.

    # Создадим произвольный экземпляр
    instance = Foo(i=1)

    # Для теста, изменим значение поля на любое, отличное от True
    instance._replace = False

    # Вызовем метод
    instance._init_validation()

    # Значение у _replace должно вновь стать True
    assert instance._replace


def test_init_field_validation():
    """
        Тест инициализации свойст для валидации поля.
    """
    # Для валидации поля экземпляра класса InstanceValidation, дополнительно к
    # свойствам родителя, свойство self._replacement инициализируется
    # значением None.

    # Создадим произвольный экземпляр
    instance = Foo(i=1)

    # Для теста, изменим значение поля на любое, отличное от None
    instance._replacement = 'data'

    # Для вызова метода нужен экземпляр поля датакласса
    field = fields(instance)[0]

    # Вызовем метод
    instance._init_field_validation(field)

    # Значение у _replace должно вновь стать None
    assert instance._replacement is None


'''
    # Если это свойство установлено в True, то, при успехе валидации, если
    # значение поля - словарь, а анотация к полю - класс-потомок
    # InstanceValidation, будет произведена замена словаря на экземпляр класса
    # из аннотации.
'''
