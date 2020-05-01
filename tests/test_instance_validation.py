from dataclasses import dataclass, fields

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

    # Значение у _replacement должно вновь стать None
    assert instance._replacement is None


def test_try_replacing_successfully():
    """
        Тест вызова _try_replacing() который завершился заменой значения
    """
    # Создадим экземпляр с полем, которое имеет аннотацию
    # датаклассом-потомком InstanceValidation,
    instance = Bar(foo=Foo(i=1))

    # Изменим значение поля foo на словарь (на самом деле, здесь, в тесте,
    # можно подставить любое значение, но при использовании класса это
    # будет именно словарь)
    data = {'i': 2}
    instance.foo = data

    # Для наглядности, присвоим полю self._replace значение True
    # (это значение по умолчанию, но именно оно необходимо для возможности
    # произвести замену)
    instance._replace = True  # Выполнять замену, если есть на что

    # В поле self._replacement должен быть подготовленный экземпляр, который
    # был получен из словаря
    instance._replacement = Foo(**data)

    # Вызовем метод
    instance._try_replacing()

    # Должна произойти замена значения поля
    assert instance.foo == instance._replacement


def test_try_replacing_unsuccessfully():
    """
        Тест вызова _try_replacing() который НЕ завершился заменой значения
    """
    # Создадим экземпляр с полем, которое имеет аннотацию
    # датаклассом-потомком InstanceValidation,
    instance = Bar(foo=Foo(i=1))

    # Изменим значение поля foo на словарь (на самом деле, здесь, в этом тесте,
    # можно подставить любое значение, но при использовании класса это
    # будет именно словарь)
    data = {'i': 2}
    instance.foo = data

    # 1. Присвоим полю self._replace значение False
    instance._replace = False  # Не выполнять замену

    # В поле self._replacement должен быть подготовленный экземпляр, который
    # был получен из словаря
    instance._replacement = Foo(**data)  # Претендент на замену

    # Вызовем метод
    instance._try_replacing()

    # Значения поля должно остаться прежним
    assert instance.foo == data

    # 2. Присвоим полю self._replace значение True
    instance._replace = True  # Выполнять замену, если есть на что

    # Но в поле self._replacement поставим None (значение, которое оно
    # получает после инициализации перед валидацией поля)
    instance._replacement = None  # Нет значения для замены

    # Вызовем метод
    instance._try_replacing()

    # Значения поля должно остаться прежним
    assert instance.foo == data
