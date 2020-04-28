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


def test_basic_validation_not_valid():

    nocorrect_input = correct_input
    nocorrect_input['s'] = 2

    instance = Foo(**nocorrect_input)

    assert instance.get_errors()


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
