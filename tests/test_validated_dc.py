from dataclasses import dataclass
from typing import List, Optional, Union
try:
    from typing import Literal
except Exception:  # pragma: no cover
    from typing_extensions import Literal

from validated_dc import ValidatedDC


@dataclass
class Phone(ValidatedDC):
    phone: str
    kind: Literal['personal', 'work'] = 'personal'


@dataclass
class Email(ValidatedDC):
    email: str
    kind: Literal['personal', 'work'] = 'work'


@dataclass
class Address(ValidatedDC):
    city: str
    zip_code: Optional[str] = None


@dataclass
class Person(ValidatedDC):
    name: str
    age: int
    contact: Union[Phone, Email, List[Union[Phone, Email]]]
    address: Address


@dataclass
class Workers(ValidatedDC):
    person: Union[Person, List[Person]]


def test_get_nested_validated_dc():
    """
        Тест метода-класса get_nested_validated_dc().
        Он должен вернуть множество классов-потомков ValidatedDC, которые
        вложены в определениях полей текущего класса.
    """
    nested_validated_dc = set((
        Phone, Email, Address, Person
    ))

    assert Workers.get_nested_validated_dc() == nested_validated_dc
