"""
    Тесты класса TypingValidation.
"""
from dataclasses import dataclass
from typing import List, Literal, Optional, Union, Any

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
