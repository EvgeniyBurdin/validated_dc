from data_classes import ValidatedDC
from dataclasses import dataclass

from typing import List, Union, Literal, Optional


@dataclass
class Phone(ValidatedDC):
    number: str
    kind: Literal['personal', 'work'] = 'personal'


@dataclass
class Email(ValidatedDC):
    address: str
    kind: Literal['personal', 'work'] = 'work'


@dataclass
class Address(ValidatedDC):
    city: str
    zip_code: Optional[str] = None


@dataclass
class Person(ValidatedDC):
    name: str
    contact: Union[Phone, Email, List[Union[Phone, Email]]]
    address: Address


@dataclass
class Workers(ValidatedDC):
    person: Union[Person, List[Person]]


person = {
    'name': 'Ivan',
    'contact': [
        {'number': '+7-999-000-00-00'},
        {'address': 'ivan@mail.ru', 'kind': 'personal'}
    ],
    'address': {
        'city': 'Samara'
    }
}

workers = Workers(person=person)

print(workers.get_errors())
# None

print(workers)
# Workers(person=Person(name='Ivan', contact=[Phone(number='+7-999-000-00-00',
# kind='personal'), Email(address='ivan@mail.ru', kind='personal')],
# address=Address(city='Samara', zip_code=None)))


person = [
    {
        'name': 'Ivan',
        'contact': [
            {'number': '+7-999-000-00-00'},
            {'address': 'ivan@mail.ru', 'kind': 'personal'}
        ],
        'address': {
            'city': 'Samara'
        }
    },
    {
        'name': 'Peter',
        'contact': {'number': '+7-911-000-00-00'},
        'address': {'city': 'Penza', 'zip_code': '440000'}
    }
]

workers = Workers(person=person)
print(workers.get_errors())
# None

print(workers)
# Workers(person=[Person(name='Ivan', contact=[Phone(number='+7-999-000-00-00',
# kind='personal'), Email(address='ivan@mail.ru', kind='personal')],
# address=Address(city='Samara', zip_code=None)), Person(name='Peter',
# contact=Phone(number='+7-911-000-00-00', kind='personal'),
# address=Address(city='Penza', zip_code='440000'))])

print(Workers.get_nested_validated_dc())
# {<class '__main__.Phone'>, <class '__main__.Email'>,
# <class '__main__.Address'>, <class '__main__.Person'>}

person = {
    'name': 123,
    'contact': [
        {'number': '+7-999-000-00-00'},
        {'address': 'ivan@mail.ru', 'kind': 'personal'}
    ],
    'address': {
        'city': 'Samara'
    }
}

workers = Workers(person=person)

print(workers.get_errors())
# [{<class '__main__.Person'>: [{'field_name': 'name', 'field_value': 123,
# 'field_type': <class 'str'>}]}, {'field_name': 'person', 'field_value':
# {'name': 123, 'contact': [{'number': '+7-999-000-00-00'}, {'address':
# 'ivan@mail.ru', 'kind': 'personal'}], 'address': {'city': 'Samara'}},
# 'field_type': <class '__main__.Person'>}, {'field_name': 'person',
# 'field_value': {'name': 123, 'contact': [{'number': '+7-999-000-00-00'},
# {'address': 'ivan@mail.ru', 'kind': 'personal'}], 'address': {'city':
# 'Samara'}}, 'field_type': typing.List[__main__.Person]}]
