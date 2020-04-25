"""
    Утилиты для предоставления читабельных форм для  типов и данных
"""
import re
from typing import Any


def value_readable_form(value: Any) -> str:
    """
        Преобразует значение к читаемому виду.
    """
    result = value

    # Если значение строка, то заключим ее в кавычки
    if isinstance(value, str):
        result = '"%s"' % value

    return result


def type_readable_form(type_: type) -> str:
    """
        Преобразует тип к читаемому виду.
        А именно - удаляет из строкового представления типа ссылки на модули,
        где определены используемые в типе классы, и другой "шум".
    """
    if type(type_) == type:
        result = type_.__name__
    else:
        result = str(type_)

    pattern_for_delete = r'[<>\w]*\.'
    result = re.sub(pattern_for_delete, '', result)

    return result
