from validated_dc import ValidatedDC
from dataclasses import dataclass

from typing import List, Union, Literal, Optional


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


print(Workers.get_nested_validated_dc(), '\n')
# {<class '__main__.Phone'>, <class '__main__.Email'>,
# <class '__main__.Address'>, <class '__main__.Person'>}


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

print(workers.get_errors(), '\n')
# None

print(workers, '\n')
# Workers(person=Person(name='Ivan', age=30,
# contact=[Phone(phone='+7-999-000-00-00', kind='personal'), <-- 'kind' default
# Email(email='ivan@mail.ru', kind='personal'),
# Phone(phone='+7-777-000-00-00', kind='work')],
# address=Address(city='Samara', zip_code=None)))

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
print(workers.get_errors(), '\n')
# None

print(workers, '\n')
# Workers(person=[
# Person(name='Ivan', age=30, contact=[Phone(phone='+7-999-000-00-00',
# kind='personal'), Email(email='ivan@mail.ru', kind='personal'),
# Phone(phone='+7-777-000-00-00', kind='work')],
# address=Address(city='Samara', zip_code=None)),
# Person(name='Oleg', age=35, contact=Phone(phone='+7-911-000-00-00',
# kind='personal'), address=Address(city='Penza', zip_code='440000'))])

person = {
    'name': 123,  # <- Error! Not str.
    'age': 30,
    'contact': [
        {'phone': 999},  # <- Error! Not str.
        {'email': 'ivan@mail.ru', 'kind': 'personal'}
    ],
    'address': {'city': 'Samara'}
}

workers = Workers(person=person)

print(workers.get_errors(), '\n')  # Errors log:
# {'person': [InstanceValidationError(value_repr="{'name': 123, 'age':
# 30, '...}", value_type=<class 'dict'>, annotation=<class '__main__.Person'>,
#  exception=None, errors={'name': [BasicValidationError(value_repr='123',
# value_type=<class 'int'>, annotation=<class 'str'>, exception=None)],
# 'contact': [InstanceValidationError(value_repr="[{'phone': 999},
# {'email':...]", value_type=<class 'list'>,
# annotation=<class '__main__.Phone'>, exception=None, errors=None),
# InstanceValidationError(value_repr="[{'phone': 999}, {'email':...]",
# value_type=<class 'list'>, annotation=<class '__main__.Email'>,
# exception=None, errors=None), InstanceValidationError(value_repr=
# "{'phone': 999}", value_type=<class 'dict'>, annotation=
# <class '__main__.Phone'>, exception=None, errors={'phone':
# [BasicValidationError(value_repr='999', value_type=<class 'int'>,
# annotation=<class 'str'>, exception=None)]}), InstanceValidationError(
# value_repr="{'phone': 999}", value_type=<class 'dict'>, annotation=
# <class '__main__.Email'>, exception=TypeError("__init__() got an unexpected
# keyword argument 'phone'"), errors=None), ListValidationError(value_repr=
# "{'phone': 999}", value_type=<class 'dict'>, annotation=typing.Union[
# __main__.Phone, __main__.Email], exception=None, item_index=0)]}),
# BasicValidationError(value_repr="{'name': 123, 'age': 30, '...}",
# value_type=<class 'dict'>, annotation=typing.List[__main__.Person],
# exception=None)]}

# person - is still a dictionary
# change the values to valid
workers.person['name'] = 'Ivan'
workers.person['contact'][0]['phone'] = '+7-999-000-00-00'
print(workers.is_valid(), '\n')
# True

print(workers.person.name, '\n')  # person - is now an instance Person
# Ivan

person = {
    'name': 'Ivan',
    'years': 30,  # <- Error! Invalid field name.
    'contact': [
        {'phone': '+7-999-000-00-00'},
        {'email': 'ivan@mail.ru', 'kind': 'personal'}
    ],
    'address': {'city': 'Samara'}
}

workers = Workers(person=person)

print(workers.get_errors(), '\n')   # Errors log:
# {'person': [InstanceValidationError(value_repr="{'name': 'Ivan',
# 'years': ...}", value_type=<class 'dict'>, annotation=<class
# '__main__.Person'>, exception=TypeError("__init__() got an unexpected
# keyword argument 'years'"), errors=None), BasicValidationError(value_repr=
# "{'name': 'Ivan', 'years': ...}", value_type=<class 'dict'>,
# annotation=typing.List[__main__.Person], exception=None)]}
