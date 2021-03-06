"""
    Тесты класса TypingValidation.
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
try:
    from typing import Literal
except Exception:  # pragma: no cover
    from typing_extensions import Literal

import pytest

from validated_dc import STR_ALIASES, TypingValidation


@dataclass
class Phone(TypingValidation):
    phone: str
    kind: Literal['mobile', 'home'] = 'mobile'


@dataclass
class Email(TypingValidation):
    email: str
    kind: Literal['personal', 'working'] = 'personal'


@pytest.fixture()
def instance():
    """
        Возвращает валидный экземаляр Phone
    """
    return Phone(phone='79991112233')


def test_is_instance_true(instance):
    """
        Тест метода _is_instance() который вернет True
    """
    annotation = Any  # Возьмем любой поддерживаемый алиас
    value = 1
    assert instance._is_instance__vdc(value, annotation)

    annotation = Optional[int]  # и еще
    value = 1
    assert instance._is_instance__vdc(value, annotation)

    annotation = List[int]
    value = [1, ]
    assert instance._is_instance__vdc(value, annotation)

    annotation = List[Optional[int]]
    value = [1, None, ]
    assert instance._is_instance__vdc(value, annotation)

    annotation = List[Union[int, str, list]]
    value = [1, '2', [3, 4, ], ]
    assert instance._is_instance__vdc(value, annotation)

    # и т.д. и т.п...
    # Можно использовать любой поддерживаемый алиас в любой допустимой
    # комбинации c любым типом... Например и так:
    annotation = List[Union[int, str, Email]]
    value = [1, '2', Email(email='mail@mail.com'), ]
    assert instance._is_instance__vdc(value, annotation)

    # А так как TypingValidation наследник InstanceValidation, то можно вместо
    # него подставить словарь:
    value = [1, '2', {'email': 'mail@mail.com'}, ]
    assert instance._is_instance__vdc(value, annotation)


def test_is_instance_false(instance):
    """
        Тест метода _is_instance() который вернет False
    """
    annotation = List[int]
    value = ['1', ]  # Ошибка - str не int
    assert not instance._is_instance__vdc(value, annotation)

    annotation = List[Optional[int]]
    value = ['1', None, ]  # Ошибка - str не int и не None
    assert not instance._is_instance__vdc(value, annotation)

    annotation = List[Union[int, str, list]]
    value = [.1, '2', [3, 4, ], ]  # Ошибка - float не int не str и не list
    assert not instance._is_instance__vdc(value, annotation)

    annotation = List[Union[int, str, Email]]
    value = [1, '2', Email(email=12345), ]  # Ошибка - int не str
    assert not instance._is_instance__vdc(value, annotation)

    # Ошибки:
    # 1. Словарь не является допустимым типом в этом списке;
    # 2. Этот словарь нельзя использовать как входные данные для класса Email
    # так у Email нет поля с именем xxxx.
    value = [1, '2', {'xxxx': 'mail@mail.com'}, ]
    assert not instance._is_instance__vdc(value, annotation)


def test_is_instance_false_error_with_exception(instance):
    """
        Тест метода _is_instance() который вернет False, и в ошибке будет
        исключение.

        Этот метод "гасит" все исключения, но если оно случилось, то
        записывает информацию о нем в ошибку.
    """
    # Убедимся что ошибок нет
    assert not instance._field_errors__vdc

    annotation = Dict['str', 'str']  # Возьмем любой НЕподдерживаемый алиас
    value = {'1': '2'}
    # И хоть значение соответствует аннотации,
    # метод _is_instance() должен вернуть False
    assert not instance._is_instance__vdc(value, annotation)
    # ... а список ошибок должен пополниться одной ошибкой, которая,
    # в том числе, имеет и информацию об исключении
    assert instance._field_errors__vdc[0].exception


def test_is_typing_alias(instance):
    """
        Тест метода _is_typing_alias() который возвращает True если
        аннотация - из модуля typing, и False если нет.
    """
    # Метод должен вернуть True
    annotation = str(List[int])  # Поддерживаемый алиас из typing
    assert instance._is_typing_alias(annotation)
    annotation = str(Dict[int, int])  # НЕ поддерживаемый алиас из typing
    assert instance._is_typing_alias(annotation)

    # Метод должен вернуть False
    annotation = str(int)
    assert not instance._is_typing_alias(annotation)
    annotation = str(Email)
    assert not instance._is_typing_alias(annotation)


def test_is_supported_alias(instance):
    """
        Тест метода _is_supported_alias() который возвращает True если
        аннотация из модуля typing поддерживается валидацией класса, и
        False если нет.
    """
    for str_alias in STR_ALIASES.values():
        assert instance._is_supported_alias(str_alias)

    assert not instance._is_supported_alias(str(Dict[int, int]))


def test_is_union_instance(instance):
    """
        Тест метода _is_union_instance() который возвращает True если
        значение имеет тип одного из типов кортежа Union, и False если нет.
    """
    annotation = Optional[int]
    value = 1
    assert instance._is_union_instance(value, annotation)
    value = None
    assert instance._is_union_instance(value, annotation)
    value = 0.3  # Ошибка - float не int и не None
    assert not instance._is_union_instance(value, annotation)

    annotation = Union[int, str]
    value = 1
    assert instance._is_union_instance(value, annotation)
    value = '2'
    assert instance._is_union_instance(value, annotation)
    value = 0.3  # Ошибка - float не int и не  str
    assert not instance._is_union_instance(value, annotation)

    # Union так же может иметь вложенные поддерживаемые алиасы из typing
    annotation = Union[List[int], str]
    value = [1, 2, ]
    assert instance._is_union_instance(value, annotation)
    value = '1'
    assert instance._is_union_instance(value, annotation)
    value = [1, '2', ]   # Ошибка - элемент списка может быть только int
    assert not instance._is_union_instance(value, annotation)

    # Union сам может быть вложенныи в другой поддерживаемый алиас из typing
    annotation = Union[List[Union[int, str]], str]
    value = [1, '2', ]
    assert instance._is_union_instance(value, annotation)
    value = '1'
    assert instance._is_union_instance(value, annotation)
    value = [1, '2', 0.3]  # Ошибка - элемент списка может быть int или str
    assert not instance._is_union_instance(value, annotation)

    # Так как TypingValidation наследник InstanceValidation, то следующий
    # вызов так же вернет True
    annotation = Union[List[Union[int, Email]], str]
    value = [1, {'email': 'mail@mail.com'}, 2, Email(email='mail2@mail.com')]
    assert instance._is_union_instance(value, annotation)

    # а здесь - вернет False т.к. поля xxxx нет в классе Email
    value = [1, {'xxxx': 'mail@mail.com'}, 2, Email(email='mail2@mail.com')]
    assert not instance._is_union_instance(value, annotation)
    # и здесь - вернет False т.к. email должен быть строкой
    value = [1, {'email': 12345}, 2, Email(email='mail2@mail.com')]
    assert not instance._is_union_instance(value, annotation)
    value = [1, {'email': 'mail@mail.com'}, 2, Email(email=12345)]
    assert not instance._is_union_instance(value, annotation)


def test_is_list_instance(instance):
    """
        Тест метода _is_list_instance() который возвращает True если
        все элементы списка имеет тип указанный в List, и False если нет.
    """
    annotation = List[int]
    value = [1, 2, ]
    assert instance._is_list_instance(value, annotation)
    value = [1, '2', ]
    assert not instance._is_list_instance(value, annotation)
    value = 1
    assert not instance._is_list_instance(value, annotation)

    annotation = List[List[int]]
    value = [[1, 2, ], [3, 4, ]]
    assert instance._is_list_instance(value, annotation)
    value = [[1, 2, ], [3, '4', ]]
    assert not instance._is_list_instance(value, annotation)


def test_is_literal_instance(instance):
    """
        Тест метода _is_literal_instance() который возвращает True если
        значение присутствует в кортеже Literal, и False если нет.
    """
    annotation = Literal[1, 2]
    value = 1
    assert instance._is_literal_instance(value, annotation)
    value = 2
    assert instance._is_literal_instance(value, annotation)
    value = '2'
    assert not instance._is_literal_instance(value, annotation)
    value = 3
    assert not instance._is_literal_instance(value, annotation)


def test_is_any_instance(instance):
    """
        Тест метода _is_any_instance() который возвращает True всегда
    """
    annotation = Any
    value = 1
    assert instance._is_any_instance(value, annotation)
    value = '1'
    assert instance._is_any_instance(value, annotation)
    value = Email
    assert instance._is_any_instance(value, annotation)
    value = True
    assert instance._is_any_instance(value, annotation)
    value = int
    assert instance._is_any_instance(value, annotation)
