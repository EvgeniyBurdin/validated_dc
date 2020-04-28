from dataclasses import dataclass

from validated_dc import BasicValidation


class СustomСlass:

    foo = 'foo'

    def bar(self):
        pass


@dataclass
class Foo(BasicValidation):
    i: int
    s: str
    l: list
    # ... You can use all other standard python classes.
    cc: СustomСlass


correct_input = {
    'i': 1,
    's': '2',
    'l': [3, '4'],
    'cc': СustomСlass()
}


def test_basic_validation_valid():

    instance = Foo(**correct_input)

    assert instance.get_errors() is None
    assert instance.is_valid()


def test_basic_validation_not_valid():

    nocorrect_input = correct_input
    nocorrect_input['s'] = 2
    nocorrect_input['cc'] = 5

    instance = Foo(**nocorrect_input)

    # Есть ошибки в данных
    assert instance.get_errors()
    assert not instance.is_valid()

    fields_errors = set([key for key in instance.get_errors().keys()])
    # Данные в полях s и cc имеют ошибки
    assert fields_errors == set(['s', 'cc'])


def test__post_init__():
    """
        Тест запуска валидации после создания экземпляра
        (в методе self.__post_init__())
    """
    @dataclass
    class FakeBasicValidation(BasicValidation):
        """
            Подменим метод старта валидаци
        """
        def _run_validation(self):
            self.validation_run = True

    instance = FakeBasicValidation()
    assert instance.validation_run
