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
    class TypingValidation(InstanceValidation):
        Добавляет для использования в аннотациях некоторые алиасы из модуля
        typing, на данный момент это: List, Union, Optional, Any и Literal.

    @dataclass
    class InstanceValidation(BasicValidation):
        Добавляет возможность при создании экземпляра использовать словарь,
        при инициализации значения поля, вместо экземпляра потомка
        InstanceValidation указанного в аннотации поля.
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
import logging
from dataclasses import Field as DataclassesField
from dataclasses import asdict, dataclass
from dataclasses import fields as dataclasses_fields
from typing import Any, Callable, List, Optional, Union, Sequence

try:
    from typing import Literal
except Exception:  # pragma: no cover
    from typing_extensions import Literal


logger = logging.getLogger()


@dataclass
class BasicValidationError:
    value_repr: str   # Строковое представление значения или его части
    value_type: type  # Тип значения
    annotation: type  # Тип в аннотации
    exception: Optional[Exception]  # Исключение, если было


MAX_REPR = 30  # Максимальная длина строкового представления


def get_value_repr(value: Any) -> str:
    """
        Отдать строковое представление значения длиной не более MAX_REPR.
    """
    result = str(value)
    if len(result) > MAX_REPR:
        result = result[:MAX_REPR-4] + '...' + result[-1]

    return result


@dataclass
class BasicValidation:
    """
        Базовый валидируемый датакласс.

        Работает как обычный датакласс, но после создания экземпляра
        запускается валидация данных.

        Для аннотаций полей можно использовать стандартные типы Python и
        классы созданные пользователем.
    """
    def __post_init__(self) -> None:
        """
            Запускает валидацию после создания экземпляра
        """
        self._run_validation()

    def get_errors(self) -> Optional[dict]:
        """
            Возвращает словарь с ошибками валидации, или None если
            их нет (то есть - экземпляр валиден).

            Можно использовать сразу после создания экземпляра для определения
            его валидности, а так же после вызова метода is_valid(self).
        """
        logger.warning(
            "DEPRECATED: Instance method 'instance.get_errors()' is "
            "deprecated. Support for this method will end in version 2.0. "
            "Use a separate function "
            "'from validated_dc import get_errors', "
            "and 'get_errors(instance)'."
        )

        return self._errors__vdc if self._errors__vdc else None

    def is_valid(self) -> bool:
        """
            Запускает валидацию и возращает валидный экзампляр или нет.

            Можно использовать в любой момент жизни экземпляра.
        """
        logger.warning(
            "DEPRECATED: Instance method 'instance.is_valid()' is deprecated. "
            "Support for this method will end in version 2.0. "
            "Use a separate function "
            "'from validated_dc import is_valid', "
            "and 'is_valid(instance)'."
        )

        self._run_validation()

        return not bool(self._errors__vdc)

    def _init_validation(self) -> None:
        """
            Инициализация валидации
        """
        self._errors__vdc = {}

    def _is_instance__vdc(self, value: Any, annotation: type) -> bool:
        """
            Проверка значения на соответствие типу.
        """
        exception = None

        try:
            result = isinstance(value, annotation)
        except Exception as exс:
            exception = exс
            result = False

        if not result:
            self._field_errors__vdc.append(BasicValidationError(
                value_repr=get_value_repr(value), value_type=type(value),
                annotation=annotation, exception=exception
            ))

        return result

    def _init_field_validation(self, field: DataclassesField) -> None:
        """
            Инициализация валидации для текущего поля
        """
        self._field_errors__vdc = []
        self._field_name__vdc = field.name
        self._field_value__vdc = getattr(self, field.name)
        self._field_annotation__vdc = field.type

    def _is_field_valid(self, field: DataclassesField) -> bool:
        """
            Запускает проверку поля
        """
        self._init_field_validation(field)

        return self._is_instance__vdc(
            self._field_value__vdc, self._field_annotation__vdc
        )

    def _save_current_field_errors(self) -> None:
        """
            Записывает ошибки текущего поля в self._errors
            (в ошибки всего экземпляра)
        """
        self._errors__vdc[self._field_name__vdc] = self._field_errors__vdc

    def _run_validation(self) -> None:
        """
           Запускает проверку всех полей
        """
        self._init_validation()

        for field in dataclasses_fields(self):
            if not self._is_field_valid(field):
                self._save_current_field_errors()


def get_errors(instance: BasicValidation) -> Optional[Sequence]:
    """
        Отдает словарь ошибок или None если их нет.
    """
    return instance._errors__vdc if instance._errors__vdc else None


def is_valid(instance: BasicValidation) -> bool:
    """
        Запускает валидацию датакласса.
        Отдает True если датакласс валиден и False если нет.
    """
    instance._run_validation()

    return not bool(instance._errors__vdc)


# ----------------------------------------------------------------------------


@dataclass
class InstanceValidationError(BasicValidationError):
    errors: Optional[List]


@dataclass
class InstanceValidation(BasicValidation):
    """
        Добавляет возможность при создании экземпляра использовать словарь,
        при инициализации значения поля, вместо экземпляра потомка
        InstanceValidation указанного в аннотации поля.

        Это может пригодиться, например, при получении json-словаря по апи,
        для автоматической валидации значений.

        Так же, при этом, происходит замена словаря на экземпляр датакласса
        из аннотации (если данные из словаря валидны).
    """
    def _init_validation(self) -> None:

        super()._init_validation()

        # Выполнять ли замену словаря на экземпляр класса-потомка
        # InstanceValidation из аннотации поля (в случае пригодности
        # словаря для создания такого экземпляра), или Нет.
        self._is_replace__vdc = True

        self._replaced_field_names = []

    def _is_instance__vdc(self, value: Any, annotation: type) -> bool:

        is_type = type(annotation) == type
        if is_type and issubclass(annotation, InstanceValidation):

            exception = None
            errors = None
            instance = None

            if isinstance(value, dict) or isinstance(value, annotation):

                if isinstance(value, annotation):
                    value = asdict(value)

                try:
                    instance = annotation(**value)
                    errors = instance._errors__vdc if instance._errors__vdc \
                        else None
                except Exception as exc:
                    exception = exc

                if errors is None and exception is None:
                    self._replacement__vdc = instance
                    return True

                self._field_errors__vdc.append(InstanceValidationError(
                    value_repr=get_value_repr(value), value_type=type(value),
                    annotation=annotation, exception=exception, errors=errors
                ))
                return False

        return super()._is_instance__vdc(value, annotation)

    def _init_field_validation(self, field: DataclassesField) -> None:

        super()._init_field_validation(field)

        # Свойство предназначенное для замены словаря
        self._replacement__vdc = None

    def _try_replacing(self) -> None:
        """
            Пытается заменить значение у текущего поля на текущее значение
            свойства self._replacement__vdc.
        """
        # Если включен флаг замены и есть чем заменять, то установим
        # новое значение у поля
        if self._is_replace__vdc and self._replacement__vdc is not None:
            setattr(self, self._field_name__vdc, self._replacement__vdc)
            self._replaced_field_names.append(self._field_name__vdc)

    def _is_field_valid(self, field: DataclassesField) -> bool:

        result = super()._is_field_valid(field)

        if result:
            # Попробуем произвести замену
            self._try_replacing()

        return result


# ----------------------------------------------------------------------------


# Строковые представления для всех поддерживаемых алиасов:
STR_ALIASES = {
    List: str(List),
    Union: str(Union),
    Optional: str(Optional),
    Any: str(Any),
    Literal: str(Literal)
}


@dataclass
class TypingValidationError(BasicValidationError):
    pass


@dataclass
class ListValidationError:
    item_index: int
    item_repr:  str   # Строковое представление элемента или его части
    item_type:  type  # Тип элемента
    annotation: type  # Тип в аннотации


@dataclass
class LiteralValidationError:
    literal_repr: str   # Строковое представление литерала или его части
    literal_type: type  # Тип литерала
    annotation: type    # Тип в аннотации


@dataclass
class TypingValidation(InstanceValidation):
    """
        Добавляет для использования в аннотациях некоторые алиасы из модуля
        typing.

        Поддерживаемые алиасы перечислены в константе STR_ALIASES.
    """
    def _is_instance__vdc(self, value: Any, annotation: type) -> bool:

        str_annotation = str(annotation)

        if self._is_typing_alias(str_annotation):

            if not self._is_supported_alias(str_annotation):

                exception = TypeError('Alias is not supported!')
                self._field_errors__vdc.append(TypingValidationError(
                    value_repr=get_value_repr(value), value_type=type(value),
                    annotation=annotation, exception=exception
                ))
                return False

            is_instance = self._get_alias_method(str_annotation)

            if is_instance is not None:
                self._typing_field_error = None
                result = is_instance(value, annotation)
                if result:
                    return True
                else:
                    if self._typing_field_error is not None:
                        self._field_errors__vdc.append(
                            self._typing_field_error
                        )
                        self._typing_field_error = None
                    return False

        return super()._is_instance__vdc(value, annotation)

    @staticmethod
    def _is_typing_alias(annotation: str) -> bool:
        """
            Проверяет является ли annotation алиасом из модуля typing
        """
        str_aliases = STR_ALIASES.values()
        prefixes = [alias[:alias.find('.')] for alias in str_aliases]
        return annotation.startswith(tuple(prefixes))

    @staticmethod
    def _is_supported_alias(annotation: str) -> bool:
        """
            Проверяет является ли annotation поддерживаемым алиасом
        """
        for str_alias in STR_ALIASES.values():
            if annotation.startswith(str_alias):
                return True
        return False

    def _get_alias_method(self, annotation: str) -> Optional[Callable]:
        """
            Возавращает метод для проверки алиаса
        """

        if annotation.startswith(STR_ALIASES[Union]) or \
           annotation.startswith(STR_ALIASES[Optional]):
            return self._is_union_instance

        elif annotation.startswith(STR_ALIASES[List]):
            return self._is_list_instance

        elif annotation.startswith(STR_ALIASES[Literal]):
            return self._is_literal_instance

        elif annotation.startswith(STR_ALIASES[Any]):
            return self._is_any_instance

    def _is_union_instance(self, value: Any, annotation: type) -> bool:
        """
            Валидация на алиасы Optional и Union.

            Проверяет является ли value экземпляром одного из типов из
            кортежа.
        """
        # У Union допустимые типы перечислены в кортеже __args__
        for item_annotation in annotation.__args__:
            if self._is_instance__vdc(value, item_annotation):
                return True
        # Нет ни одного типа, подходящего для value
        return False

    def _is_list_instance(self, value: Any, annotation: type) -> bool:
        """
            Валидация на алиас List.

            Проверяет является ли value списком экземпляров annotation.
        """
        if isinstance(value, list):
            # Имеем дело со списком. В родительском классе возможна замена
            # значения-словаря на значение-экземпляр потомка родительского
            # класса. То есть, возможно изменение списка значений текущего
            # поля.
            # Будем к этому готовы.
            new_value = []

            # У List допустимый тип стоит первым в кортеже __args__
            annotation = annotation.__args__[0]
            for i, item_value in enumerate(value):
                if self._is_instance__vdc(item_value, annotation):
                    # Собираем новый список для текущего поля
                    # (так как в нем возможна замена элемента-словаря на
                    # элемент-экземпляр потомка родительского класса)
                    if self._replacement__vdc:
                        item_value = self._replacement__vdc
                        self._replacement__vdc = False
                    new_value.append(item_value)
                else:
                    self._typing_field_error = ListValidationError(
                        item_index=i, item_repr=get_value_repr(item_value),
                        item_type=type(item_value), annotation=annotation
                    )
                    return False

            # Все элементы списка value валидные.
            self._replacement__vdc = new_value
            return True

        self._typing_field_error = BasicValidationError(
            value_repr=get_value_repr(value), value_type=type(value),
            annotation=annotation, exception=None
        )

        return False

    def _is_literal_instance(self, value: Any, annotation: type) -> bool:
        """
            Валидация на алиас Literal.

            Проверяет является ли value одним из annotation.__args__
        """
        result = value in annotation.__args__

        if not result:
            self._typing_field_error = LiteralValidationError(
                literal_repr=get_value_repr(value), literal_type=type(value),
                annotation=annotation
            )

        return result

    def _is_any_instance(self, value: Any, type_: type) -> bool:
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
