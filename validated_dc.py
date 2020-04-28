"""
    Валидируемые датаклассы.

    У полей класса проверяется соответствие значений их аннотациям.

    Датаклассы:

    @dataclass
    class ValidatedDC(TypingValidation):
        Датакласс с самыми полными возможностями валидации.
        Добавляет в базовый класс метод get_nested_validated_dc(cls),
        который позволяет получать все вложенные датаклассы-потомки
        ValidatedDC, которые используются в аннотациях полей.

    @dataclass
    class TypingValidation(DictReplaceableValidation):
        Добавляет для использования в аннотациях некоторые алиасы из модуля
        typing, на данный момент это: List, Union, Optional, Any и Literal.

    @dataclass
    class DictReplaceableValidation(BasicValidation):
        Добавляет возможность при создании экземпляра использовать словарь,
        при инициализации значения поля, вместо экземпляра потомка
        DictReplaceableValidation указанного в аннотации поля.
        Это может пригодиться, например, при получении json-словаря по апи,
        для автоматической валидации значений.
        Так же, при этом, происходит замена словаря на экземпляр датакласса
        из аннотации (если данные из словаря валидны).

    @dataclass
    class BasicValidation:
        Базовый валидируемый датакласс.
        Работает как обычный датакласс, но после создания экземпляра
        запускается валидация данных.
        Для аннотаций полей можно использовать стандартные типы Python и
        классы созданные пользователем.
"""
import copy
from dataclasses import Field as DataclassesField
from dataclasses import dataclass, asdict
from dataclasses import fields as dataclasses_fields
from typing import Any, Callable, List, Literal, Optional, Union


__version__ = '0.1'


@dataclass
class BasicValidation:
    """
        Базовый валидируемый датакласс.

        Работает как обычный датакласс, но после создания экземпляра
        запускается валидация данных.

        Для аннотаций полей можно использовать стандартные типы Python и
        классы созданные пользователем.

        Публичные методы:

        get_errors(self) - Отдает словарь ошибок или None если их нет.
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

    def _init_validation(self) -> None:
        """
            Устанавливает свойства используемые при валидации
        """
        self._errors = {}

    def _is_instance(self, field_value: Any, field_type: type) -> bool:
        """
            Проверка значения на соответствие типу.
        """
        try:
            result = isinstance(field_value, field_type)

        except Exception as ex:
            self._field_exception = ex
            result = False

        if not result:
            self._field_errors.append(
                (field_value, field_type)
            )

        return result

    def _field_validation(self, field: DataclassesField) -> bool:
        """
            Устанавливает свойства для текущего поля и вызывает проверку.
        """
        self._field_errors = []
        self._field_exception = None
        self._field_name = field.name
        self._field_value = getattr(self, field.name)
        self._field_type = field.type

        result = self._is_instance(self._field_value, self._field_type)

        if not result:
            # Если проверка поля завершилась неудачно, то добавим список
            # ошибок поля в ошибки всего экземпляра.
            errors = {
                'VALUE': self._field_value,
                'TYPE': self._field_type
            }
            if self._field_exception is not None:
                errors['EXCEPTION'] = self._field_exception
            else:
                errors['ERRORS'] = self._field_errors

            self._errors[self._field_name] = errors

        return result

    def _run_validation(self) -> None:
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
        Добавляет возможность при создании экземпляра использовать словарь,
        при инициализации значения поля, вместо экземпляра потомка
        DictReplaceableValidation указанного в аннотации поля.

        Это может пригодиться, например, при получении json-словаря по апи,
        для автоматической валидации значений.

        Так же, при этом, происходит замена словаря на экземпляр датакласса
        из аннотации (если данные из словаря валидны).
    """
    def _init_validation(self) -> None:
        """
            Устанавливает свойства используемые при валидации
        """
        super()._init_validation()
        self._replace = True

    def _is_instance(self, field_value: Any, field_type: type) -> bool:

        if type(field_type) == type and \
           issubclass(field_type, DictReplaceableValidation):

            if isinstance(field_value, dict) or \
               isinstance(field_value, field_type):

                if isinstance(field_value, field_type):
                    value = asdict(field_value)
                else:
                    value = field_value

                try:
                    instance = field_type(**value)
                    errors = instance.get_errors()

                except Exception as ex:
                    self._field_exception = ex
                    errors = []

                if errors is None:
                    self._replacement = instance
                    return True

                elif errors:
                    self._field_errors.append({instance.__class__: errors})
                    return False

        return super()._is_instance(field_value, field_type)

    def _field_validation(self, field: DataclassesField) -> bool:

        self._replacement = False
        result = super()._field_validation(field)
        if self._replace and result and self._replacement:
            # Если валидация поля прошла успешно и текущее значение у поля
            # изменилось, то установим новое значение у поля
            setattr(self, self._field_name, self._replacement)

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
        Добавляет для использования в аннотациях некоторые алиасы из модуля
        typing.

        Поддерживаемые алиасы перечислены в константе STR_ALIASES.
    """
    def _is_instance(self, field_value: Any, field_type: type) -> bool:

        str_field_type = str(field_type)

        if self._is_typing_alias(str_field_type):

            if self._is_supported_alias(str_field_type):
                is_instance = self._get_alias_method(str_field_type)
                result = is_instance(field_value, field_type)
                if result:
                    return True
                else:
                    self._field_errors.append((field_value, field_type))
                    return False
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
            # Имеем дело со списком. В родительском классе возможна замена
            # значения-словаря на значение-экземпляр потомка родительского
            # класса. То есть, возможно изменение списка значений текущего
            # поля.
            # Будем к этому готовы.
            new_field_value = []

            # У List допустимый тип стоит первым в кортеже __args__
            field_type = field_type.__args__[0]
            for item_value in field_value:

                if self._is_instance(item_value, field_type):
                    # Собираем новый список для текущего поля
                    # (так как в нем возможна замена элемента-словаря на
                    # элемент-экземпляр потомка родительского класса)
                    if self._replacement:
                        value = self._replacement
                        self._replacement = False
                    else:
                        value = item_value

                    new_field_value.append(value)

                else:
                    return False

            # Все элементы списка field_value валидные.
            self._replacement = new_field_value

            return True

        else:
            # Значение поля - не список, а это ошибка валидации
            return False

    def _is_literal_instance(self, field_value: Any, field_type: type) -> bool:
        """
            Валидация на алиас Literal.

            Проверяет является ли field_value одним из field_type.__args__
        """
        return field_value in field_type.__args__

    def _is_any_instance(self, field_value: Any, field_type: type) -> bool:
        """
            Валидация на алиас Any.

            Просто вернем True
        """
        return True


# ----------------------------------------------------------------------------


@dataclass
class ValidatedDC(TypingValidation):
    """
        Добавляет в базовый класс метод get_nested_validated_dc(cls),
        который позволяет получать все вложенные датаклассы-потомки
        ValidatedDC, которые используются в аннотациях полей.
    """
    @classmethod
    def get_nested_validated_dc(cls) -> set:
        """
            Отдает все, используемые полями, датаклассы ValidatedDC
        """

        def get_field_validated_dc(annotation, set_validated_dc=None) -> set:
            """
                Возвращает все ValidatedDC классы которые используются в
                аннотации у поля.
            """
            if set_validated_dc is None:
                set_validated_dc = set()

            if cls._is_typing_alias(str(annotation)):
                if hasattr(annotation, '__args__'):
                    for item in annotation.__args__:
                        get_field_validated_dc(item, set_validated_dc)
            elif type(annotation) == type and \
                    issubclass(annotation, ValidatedDC):

                set_validated_dc.add(annotation)

            return set_validated_dc

        local_validated_dc = set()
        for field in dataclasses_fields(cls):
            local_validated_dc.update(get_field_validated_dc(field.type))

        nested_validated_dc = copy.copy(local_validated_dc)

        for validated_dc in local_validated_dc:
            nested_validated_dc.update(validated_dc.get_nested_validated_dc())

        return nested_validated_dc


# ----------------------------------------------------------------------------


if __name__ == "__main__":

    @dataclass
    class SimpleInt(ValidatedDC):
        i: int

    @dataclass
    class SimpleStr(ValidatedDC):
        s: str

    @dataclass
    class SimpleDict(ValidatedDC):
        d: dict

    @dataclass
    class SimpleUnion(ValidatedDC):
        u: List[List[Union[SimpleInt, SimpleStr, SimpleDict]]]

    u = SimpleUnion(u=[
        [{'i': 1}, {'s': '1'}, {'i': 2}, {'d': {}}],
        [{'i': 5}, {'s': '6'}, {'i': 7}, {'d': {8: 8}}],
    ])

    print(u.get_errors())
    # None

    print(u)
    # SimpleUnion(u=[[SimpleInt(i=1), SimpleStr(s='1'), SimpleInt(i=2),
    #             SimpleDict(d={})], [SimpleInt(i=5), SimpleStr(s='6'),
    #             SimpleInt(i=7), SimpleDict(d={8: 8})]])

    print(SimpleUnion.get_nested_validated_dc())
    # {<class '__main__.SimpleInt'>, <class '__main__.SimpleStr'>,
    #  <class '__main__.SimpleDict'>}
