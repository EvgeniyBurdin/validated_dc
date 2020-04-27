from dataclasses import dataclass

from validated_dc import BasicValidation


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
