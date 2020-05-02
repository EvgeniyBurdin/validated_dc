"""
    Тесты класса TypingValidation.
"""
from dataclasses import dataclass
from typing import List, Literal, Optional, Union, Any, Dict

from validated_dc import TypingValidation


@dataclass
class Phone(TypingValidation):
    phone: str
    kind: Literal['mobile', 'home'] = 'mobile'


@dataclass
class Email(TypingValidation):
    email: str
    kind: Literal['personal', 'working'] = 'personal'


@dataclass
class Address(TypingValidation):
    city: str
    zip_code: Optional[str] = None


@dataclass
class Person(TypingValidation):
    name: str
    age: int
    contact: Union[Phone, Email, List[Union[Phone, Email]]]
    address: Address
    extra: Any


def test_is_instance_true():
    """
        Тест метода _is_instance() который вернет True
    """
    # Возьмем любой экземпляр
    instance = Phone(phone='79991112233')

    annotation = Any  # Возьмем любой поддерживаемый алиас
    value = 1
    assert instance._is_instance(value, annotation)

    annotation = List[int]  # Еще раз
    value = [1, ]
    assert instance._is_instance(value, annotation)

    annotation = List[Optional[int]]  # Еще раз
    value = [1, None, ]
    assert instance._is_instance(value, annotation)

    annotation = List[Union[int, str, list]]  # Еще раз
    value = [1, '2', [3, 4, ], ]
    assert instance._is_instance(value, annotation)

    # и т.д. и т.п...
    # Можно использовать любой поддерживаемый алиас в любой допустимой
    # комбинации c любым типом... Например и так:
    annotation = List[Union[int, str, Email]]
    value = [1, '2', Email(email='mail@mail.com'), ]
    assert instance._is_instance(value, annotation)

    # А так как TypingValidation наследник InstanceValidation, то можно вместо
    # него подставить словарь:
    value = [1, '2', {'email': 'mail@mail.com'}, ]
    assert instance._is_instance(value, annotation)


def test_is_instance_false():
    """
        Тест метода _is_instance() который вернет False
    """
    # Возьмем любой экземпляр
    instance = Phone(phone='79991112233')

    annotation = List[int]
    value = ['1', ]  # Ошибка - str вместо int
    assert not instance._is_instance(value, annotation)

    annotation = List[Optional[int]]
    value = ['1', None, ]  # Ошибка - str вместо int
    assert not instance._is_instance(value, annotation)

    annotation = List[Union[int, str, list]]
    value = [.1, '2', [3, 4, ], ]  # Ошибка - float вместо int
    assert not instance._is_instance(value, annotation)

    annotation = List[Union[int, str, Email]]
    value = [1, '2', Email(email=12345), ]  # Ошибка - int вместо str
    assert not instance._is_instance(value, annotation)

    # Ошибки:
    # 1. Словарь не является допустимым типом в этом списке;
    # 2. Этот словарь нельзя использовать как входные данные для класса Email
    # так у Email нет поля с именем xxxx.
    value = [1, '2', {'xxxx': 'mail@mail.com'}, ]
    assert not instance._is_instance(value, annotation)

    # и т.д. и т.п...
    # Можно использовать любой поддерживаемый алиас.


def test_is_instance_false_error_with_exception():
    """
        Тест метода _is_instance() который вернет False, и в ошибке будет
        исключение.

        Этот метод "гасит" все исключения, но если оно случилось, то
        записывает информацию о нем в ошибку.
    """
    # Возьмем любой экземпляр
    instance = Phone(phone='79991112233')

    # Убедимся что ошибок нет
    assert not instance._field_errors

    annotation = Dict['str', 'str']  # Возьмем любой НЕподдерживаемый алиас
    value = {'1': '2'}
    # И хоть значение соответствует аннотации,
    # метод _is_instance() должен вернуть False
    assert not instance._is_instance(value, annotation)
    # ... а список ошибок должен пополниться одной ошибкой, которая,
    # в том числе, имеет и информацию об исключении
    assert instance._field_errors[0].exception
