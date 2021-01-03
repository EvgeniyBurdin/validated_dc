from validated_dc import ValidatedDC
from dataclasses import dataclass

from typing import List, Union, Optional
try:
    from typing import Literal
except Exception:  # pragma: no cover
    from typing_extensions import Literal


# --- Data schema ---

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


# --- Component data schemas (e.g. for documentation)

nested_validated_dc = set([Phone, Email, Address, Person])
assert Workers.get_nested_validated_dc() == nested_validated_dc

# --- Valid input ---

person = {
    'name': 'Ivan',
    'age': 30,
    'contact': [
        {'phone': '+7-999-000-00-00'},
        {'email': 'ivan@mail.ru', 'kind': 'personal'},
        {'phone': '+7-777-000-00-00', 'kind': 'work'}
    ],
    'address': {'city': 'Samara'}
}
workers = Workers(person=person)
assert workers.get_errors() is None

# --- Valid input ---

person = [
    {
        'name': 'Ivan',
        'age': 30,
        'contact': [
            {'phone': '+7-999-000-00-00'},
            {'email': 'ivan@mail.ru', 'kind': 'personal'},
            {'phone': '+7-777-000-00-00', 'kind': 'work'}
        ],
        'address': {'city': 'Samara'}
    },
    {
        'name': 'Oleg',
        'age': 35,
        'contact': {'phone': '+7-911-000-00-00'},
        'address': {'city': 'Penza', 'zip_code': '440000'}
    }
]
workers = Workers(person=person)
assert workers.get_errors() is None

# --- Errorr input ---

person = {
    'name': 123,  # <- Error! Not str.
    'age': 30,
    'contact': [
        {'phone': 999},  # <-- Error! Not str.
        {'email': 'ivan@mail.ru', 'kind': 'personal'}
    ],
    'address': {'city': 'Samara'}
}

workers = Workers(person=person)
assert workers.get_errors()

# person - is still a dictionary
# Fix it: change the values to valid
workers.person['name'] = 'Ivan'
workers.person['contact'][0]['phone'] = '+7-999-000-00-00'
assert workers.is_valid()
assert workers.person.name  # person - is now an instance Person

# --- Errorr input ---

person = {
    'name': 'Ivan',
    'years': 30,  # <-- Error! Invalid field name.
    'contact': [
        {'phone': '+7-999-000-00-00'},
        {'email': 'ivan@mail.ru', 'kind': 'personal'}
    ],
    'address': {'city': 'Samara'}
}

workers = Workers(person=person)
assert workers.get_errors()
