"""
    Валидируемые датаклассы.

    У полей класса проверяется соответствие значений их аннотациям.
"""
from dataclasses import Field as DataclassesField
from dataclasses import dataclass
from dataclasses import fields as dataclasses_fields
from typing import Any, Callable, List, Literal, Optional, Union

from utils import value_readable_form


@dataclass
class BasicValidation:
    """
        Базовый валидируемый датакласс.

        Работает как обычный датакласс, но после создания экземпляра
        запускается валидация данных.

        Для аннотаций полей можно использовать стандартные типы Python и
        классы созданные пользователем.

        Публичные методы:

        get_errors(self) - Отдает список ошибок или None если их нет.
        is_valid(self)   - Запускает валидацию датакласса.
                           Отдает True если датакласс валиден и False если нет.
    """
    def __post_init__(self) -> None:
        """
            Запускает валидацию после создания экземпляра
        """
        self._run_validation()

    def get_errors(self) -> Optional[list]:
        """
            Возвращает список с ошибками валидации, или None если
            валидация данных прошла успешна.

            Можно использовать сразу после создания экземпляра для определения
            его валидности, а так же после вызова метода is_valid(self).
        """

        return self._errors if self._errors else None

    def is_valid(self) -> bool:
        """
            Запускает валидацию и возращает валидный экзампляр или нет.

            Можно использовать в любой момент жизни экземпляра.
        """
        self._run_validation()

        return not bool(self._errors)

    def _init_validation(self):
        """
            Устанавливает свойства используемые при валидации
        """
        self._errors = []

    def _save_error(self, **kwargs):
        """
            Добавляет ошибку в список ошибок у поля.
        """
        error = {
            'field_name': self.field_name,
            'field_value': value_readable_form(self.field_value),
            'field_type': self.field_type
        }
        if self.field_exception is not None:
            error['field_exception'] = self.field_exception

        # Если в метод передали дополнительные поля для ошибки, или имеющиеся
        # поля но с другими значениями, то сообщение об ошибке
        # дополнится/изменится.
        error.update(kwargs)

        self.field_errors.append(error)

    def _is_instance(self, field_value: Any, field_type: type) -> bool:
        """
            Проверка значения на соответствие типу.
        """
        try:
            result = isinstance(field_value, field_type)

        except Exception as error:
            self.field_exception = error
            result = False

        if not result:
            self._save_error(field_value=field_value, field_type=field_type)

        return result

    def _field_validation(self, field: DataclassesField) -> bool:
        """
            Устанавливает свойства для текущего поля и вызывает проверку.
        """
        self.field_errors = []
        self.field_exception = None
        self.field_name = field.name
        self.field_value = getattr(self, field.name)
        self.field_type = field.type

        result = self._is_instance(self.field_value, self.field_type)

        if not result:
            # Если проверка поля завершилась неудачно, то добавим список
            # ошибок поля в список ошибок всего экземпляра.
            self._errors.extend(self.field_errors)

        return result

    def _run_validation(self):
        """
            Запускает валидацию полей
        """
        self._init_validation()

        for field in dataclasses_fields(self):
            self._field_validation(field)


# ----------------------------------------------------------------------------


@dataclass
class DictReplaceableValidation(BasicValidation):
    """
        Датакласс добавляющий возможность замены словаря на экземпляр потомка
        DictReplaceableValidation, если словарь может быть использован для
        инициализации экземпляр.
    """
    def _is_instance(self, field_value: Any, field_type: type):

        if type(field_type) == type and \
           issubclass(field_type, DictReplaceableValidation):

            if isinstance(field_value, dict):
                try:
                    instance = field_type(**field_value)
                    errors = instance.get_errors()

                    self.field_exception = None

                except Exception as ex:
                    self.field_exception = ex
                    errors = []

                if errors is None:
                    self.new_field_value = instance

                    return True

                elif errors:
                    self.field_errors.append({instance.__class__: errors})

        return super()._is_instance(field_value, field_type)

    def _field_validation(self, field: DataclassesField) -> bool:

        self.new_field_value = getattr(self, field.name)
        result = super()._field_validation(field)
        if result:
            # Если валидация поля прошла успешно, то установим новое значение
            # у поля.
            setattr(self, self.field_name, self.new_field_value)

        return result


# ----------------------------------------------------------------------------


# Строковые представления для всех поддерживаемых алиасов:
STR_ALIASES = {
    List: str(List),
    Union: str(Union),
    Optional: str(Union),  # Представление как и у Union
    Any: str(Any),
    Literal: str(Literal)
}


@dataclass
class TypingValidation(DictReplaceableValidation):
    """
        Добавляет поддержку некоторых алиасов из модуля typing для аннотации
        полей валидируемого датакласса.

        Поддерживаемые алиасы перечислены в константе STR_ALIASES.
    """
    def _is_instance(self, field_value: Any, field_type: type) -> bool:

        str_field_type = str(field_type)

        if self._is_typing_alias(str_field_type):

            if self._is_supported_alias(str_field_type):
                is_instance = self._get_alias_method(str_field_type)
                result = is_instance(field_value, field_type)

                if result:
                    self.field_errors = []

                return result

            else:
                error = '%s - not supported' % str_field_type
                raise Exception(error)

        return super()._is_instance(field_value, field_type)

    @staticmethod
    def _is_typing_alias(field_type: str) -> bool:
        """
            Проверяет является ли field_type алиасом из модуля typing
        """
        str_alias = list(STR_ALIASES.values())[0]
        prefix = str_alias[:str_alias.find('.')]
        return field_type.startswith(prefix)

    @staticmethod
    def _is_supported_alias(field_type: str) -> bool:
        """
            Проверяет является ли field_type поддерживаемым алиасом
        """
        for str_alias in STR_ALIASES.values():
            if field_type.startswith(str_alias):
                return True
        return False

    def _get_alias_method(self, field_type: str) -> Optional[Callable]:
        """
            Возавращает метод для проверки алиаса
        """

        if field_type.startswith(STR_ALIASES[Union]):
            return self._is_union_instance

        elif field_type.startswith(STR_ALIASES[List]):
            return self._is_list_instance

        elif field_type.startswith(STR_ALIASES[Literal]):
            return self._is_literal_instance

        elif field_type.startswith(STR_ALIASES[Any]):
            return self._is_any_instance

    def _is_union_instance(self, field_value: Any, field_type: type) -> bool:
        """
            Валидация на алиасы Optional и Union.

            Проверяет является ли field_value экземпляром одного из типов из
            кортежа field_type.__args__
        """
        # У Union допустимые типы перечислены в кортеже __args__
        for item_type in field_type.__args__:
            if self._is_instance(field_value, item_type):
                return True

        # Нет ни одного типа, подходящего для field_value
        return False

    def _is_list_instance(self, field_value: Any, field_type: type) -> bool:
        """
            Валидация на алиас List.

            Проверяет является ли field_value списком экземпляров field_type.
        """
        if isinstance(field_value, list):
            new_field_value = []

            # У List допустимый тип стоит первым в кортеже __args__
            field_type = field_type.__args__[0]
            for item_value in field_value:

                if self._is_instance(item_value, field_type):
                    new_field_value.append(self.new_field_value)
                else:
                    return False

            # Все элементы списка field_value валидные
            self.new_field_value = new_field_value

            return True

        else:
            self._save_error(field_value=field_value, field_type=field_type)
            return False

    def _is_literal_instance(self, field_value: Any, field_type: type) -> bool:
        """
            Валидация на алиас Literal.

            Проверяет является ли field_value одним из field_type.__args__
        """
        result = field_value in field_type.__args__

        return result

    def _is_any_instance(self, field_value: Any, field_type: type) -> bool:
        """
            Валидация на алиас Any.

            Просто вернем True
        """
        return True


if __name__ == "__main__":

    @dataclass
    class SimpleInt(TypingValidation):
        i: int

    @dataclass
    class SimpleStr(TypingValidation):
        s: str

    @dataclass
    class SimpleDict(TypingValidation):
        d: dict

    @dataclass
    class SimpleUnion(TypingValidation):
        u: List[List[Union[SimpleInt, SimpleStr, SimpleDict]]]

    u = SimpleUnion(u=[
        [{'i': 1}, {'s': '1'}, {'i': 2}, {'d': {}}],
        [{'i': 5}, {'s': '6'}, {'i': 7}, {'d': {8: 8}}],
    ])

    print(u.get_errors())
    print(u)
