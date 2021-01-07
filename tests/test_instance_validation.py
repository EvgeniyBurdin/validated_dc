"""
    Тесты класса InstanceValidation.
"""

from dataclasses import dataclass, fields

from validated_dc import InstanceValidation


@dataclass
class Foo(InstanceValidation):
    i: int


@dataclass
class Bar(InstanceValidation):
    foo: Foo


def test_is_instance_true():
    """
        Тест метода self._is_instance() когда он возвращает True
    """
    # Создадим произвольный экземпляр InstanceValidation
    @dataclass
    class MyInstanceValidation(InstanceValidation):
        # Значение по умолчанию указано для возможности создать экземпляр при
        # старте теста
        bar: Bar = None

    instance = MyInstanceValidation()

    # У этого экземпляра есть поле bar с аннотацией Bar
    annotation = Bar

    # Тогда, проверка валидности поля со следующими значеними
    # должна вернуть True:

    value = {'foo': {'i': 1}}
    assert instance._is_instance__vdc(value, annotation)

    value = Bar(foo={'i': 1})
    assert instance._is_instance__vdc(value, annotation)

    value = Bar(foo=Foo(i=1))
    assert instance._is_instance__vdc(value, annotation)


def test_is_instance_false():
    """
        Тест метода self._is_instance() когда он возвращает False
    """
    # Создадим произвольный экземпляр InstanceValidation
    @dataclass
    class MyInstanceValidation(InstanceValidation):
        # Значение по умолчанию указано для возможности создать экземпляр при
        # старте теста
        bar: Bar = None

    instance = MyInstanceValidation()

    # У этого экземпляра есть поле bar с аннотацией Bar
    annotation = Bar

    # Тогда, проверка валидности поля со следующими значеними
    # должна вернуть False:

    value = {'foo': {'i': '1'}}    # Неверный тип значение у вложенного поля i
    assert not instance._is_instance__vdc(value, annotation)

    value = {'foo': {'i_x': 1}}    # Отсутствующее имя i_x в классе Foo
    assert not instance._is_instance__vdc(value, annotation)

    value = Bar(foo={'i': [1, ]})  # Неверный тип значение у вложенного поля i
    assert not instance._is_instance__vdc(value, annotation)

    value = Bar(foo=1)             # Неверный тип значение у поля foo
    assert not instance._is_instance__vdc(value, annotation)

    value = {'foo_x': {'i': 1}}  # Отсутствующее имя foo_x в классе Bar
    assert not instance._is_instance__vdc(value, annotation)

    # ... и т.п.


def test_init_validation():
    """
        Тест инициализации свойст для валидации экземпляра.
    """
    # Для валидации экземпляра класса InstanceValidation, дополнительно к
    # свойствам родителя, свойство self._replace инициализируется
    # значением True.

    # Создадим произвольный экземпляр потомка InstanceValidation
    instance = Foo(i=1)

    # Для теста, изменим значение поля на любое, отличное от True
    instance._is_replace__vdc = False

    # Вызовем метод
    instance._init_validation()

    # Значение у _replace должно вновь стать True
    assert instance._is_replace__vdc


def test_init_field_validation():
    """
        Тест инициализации свойст для валидации поля.
    """
    # Для валидации поля экземпляра класса InstanceValidation, дополнительно к
    # свойствам родителя, свойство self._replacement__vdc инициализируется
    # значением None.

    # Создадим произвольный экземпляр потомка InstanceValidation
    instance = Foo(i=1)

    # Для теста, изменим значение поля на любое, отличное от None
    instance._replacement__vdc = 'data'

    # Для вызова метода нужен экземпляр поля датакласса
    field = fields(instance)[0]

    # Вызовем метод
    instance._init_field_validation(field)

    # Значение у _replacement должно вновь стать None
    assert instance._replacement__vdc is None


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
    instance._is_replace__vdc = True  # Выполнять замену, если есть на что

    # В поле self._replacement__vdc должен быть подготовленный экземпляр,
    # который был получен из словаря
    instance._replacement__vdc = Foo(**data)

    # Вызовем метод
    instance._try_replacing()

    # Должна произойти замена значения поля
    assert instance.foo == instance._replacement__vdc


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
    instance._is_replace__vdc = False  # Не выполнять замену

    # В поле self._replacement__vdc должен быть подготовленный экземпляр,
    # который был получен из словаря
    instance._replacement__vdc = Foo(**data)  # Претендент на замену

    # Вызовем метод
    instance._try_replacing()

    # Значения поля должно остаться прежним
    assert instance.foo == data

    # 2. Присвоим полю self._replace значение True
    instance._is_replace__vdc = True  # Выполнять замену, если есть на что

    # Но в поле self._replacement__vdc поставим None (значение, которое оно
    # получает после инициализации перед валидацией поля)
    instance._replacement__vdc = None  # Нет значения для замены

    # Вызовем метод
    instance._try_replacing()

    # Значения поля должно остаться прежним
    assert instance.foo == data


def test_is_field_valid():
    """
        Тест метода self._is_field_valid().
    """
    # После вызова метода родительского класса и если он вернул True, метод
    # в классе InstanceValidation должен вызвать метод self._try_replacing().
    # Для проверки этого функционала подменим метод _try_replacing()
    @dataclass
    class FakeInstanceValidation(InstanceValidation):
        i: int

        def _try_replacing(self) -> None:
            self._try_replacing__called = True  # Маркер вызова

    # Создадим валидный экземпляр
    instance = FakeInstanceValidation(i=1)

    # Установим в False маркер вызова
    instance._try_replacing__called = False

    # Для вызова _is_field_valid() нужено экземпляр поля, получим его
    field = fields(instance)[0]

    # Вызовем метод
    instance._is_field_valid(field)

    # Метод _try_replacing() должен быть вызван
    assert instance._try_replacing__called
