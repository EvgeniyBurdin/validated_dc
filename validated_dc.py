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
from dataclasses import Field as DataclassesField
from dataclasses import dataclass, asdict
from dataclasses import fields as dataclasses_fields
from typing import Any, Callable, List, Literal, Optional, Union


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

    def get_errors(self) -> Optional[dict]:
        """
            Возвращает словарь с ошибками валидации, или None если
            их нет (то есть - экземпляр валиден).

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
            Инициализация валидации
        """
        self._errors = {}

    def _is_instance(self, value: Any, annotation: type) -> bool:
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
            self._field_errors.append(BasicValidationError(
                value_repr=get_value_repr(value), value_type=type(value),
                annotation=annotation, exception=exception
            ))

        return result

    def _init_field_validation(self, field: DataclassesField) -> None:
        """
            Инициализация валидации для текущего поля
        """
        self._field_errors = []
        self._field_name = field.name
        self._field_value = getattr(self, field.name)
        self._field_annotation = field.type

    def _is_field_valid(self, field: DataclassesField) -> bool:
        """
            Запускает проверку поля
        """
        self._init_field_validation(field)

        return self._is_instance(self._field_value, self._field_annotation)

    def _save_current_field_errors(self) -> None:
        """
            Записывает ошибки текущего поля в self._errors
            (в ошибки всего экземпляра)
        """
        self._errors[self._field_name] = self._field_errors

    def _run_validation(self) -> None:
        """
           Запускает проверку всех полей
        """
        self._init_validation()

        for field in dataclasses_fields(self):
            if not self._is_field_valid(field):
                self._save_current_field_errors()


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
        self._replace = True

    def _is_instance(self, value: Any, annotation: type) -> bool:

        is_type = type(annotation) == type
        if is_type and issubclass(annotation, InstanceValidation):

            exception = None
            errors = None

            if isinstance(value, dict) or isinstance(value, annotation):

                if isinstance(value, annotation):
                    value = asdict(value)

                try:
                    instance = annotation(**value)
                    errors = instance.get_errors()
                except Exception as exc:
                    exception = exc

                if errors is None and exception is None:
                    self._replacement = instance
                    return True

            self._field_errors.append(InstanceValidationError(
                value_repr=get_value_repr(value), value_type=type(value),
                annotation=annotation, exception=exception, errors=errors
            ))
            return False

        return super()._is_instance(value, annotation)

    def _init_field_validation(self, field: DataclassesField) -> None:

        super()._init_field_validation(field)

        # Свойство предназначенное для замены словаря
        self._replacement = None

    def _try_replacing(self) -> None:
        """
            Пытается заменить значение у текущего поля на текущее значение
            свойства self._replacement.
        """
        # Если включен флаг замены и есть чем заменять, то установим
        # новое значение у поля
        if self._replace and self._replacement is not None:
            setattr(self, self._field_name, self._replacement)

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
    Optional: str(Union),  # Представление как и у Union
    Any: str(Any),
    Literal: str(Literal)
}


@dataclass
class TypingValidationError(BasicValidationError):
    pass


@dataclass
class ListValidationError(BasicValidationError):
    item_index: int


@dataclass
class LiteralValidationError(BasicValidationError):
    pass


@dataclass
class TypingValidation(InstanceValidation):
    """
        Добавляет для использования в аннотациях некоторые алиасы из модуля
        typing.

        Поддерживаемые алиасы перечислены в константе STR_ALIASES.
    """
    def _is_instance(self, value: Any, annotation: type) -> bool:

        str_annotation = str(annotation)

        if self._is_typing_alias(str_annotation):

            if self._is_supported_alias(str_annotation):

                is_instance = self._get_alias_method(str_annotation)

                try:
                    return is_instance(value, annotation)
                except Exception:
                    pass

            exception = TypeError('Alias is not supported!')
            self._field_errors.append(TypingValidationError(
                value_repr=get_value_repr(value), value_type=type(value),
                annotation=annotation, exception=exception
            ))
            return False

        return super()._is_instance(value, annotation)

    @staticmethod
    def _is_typing_alias(annotation: str) -> bool:
        """
            Проверяет является ли annotation алиасом из модуля typing
        """
        str_alias = list(STR_ALIASES.values())[0]
        prefix = str_alias[:str_alias.find('.')]
        return annotation.startswith(prefix)

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

        if annotation.startswith(STR_ALIASES[Union]):
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
            if self._is_instance(value, item_annotation):
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
                if self._is_instance(item_value, annotation):
                    # Собираем новый список для текущего поля
                    # (так как в нем возможна замена элемента-словаря на
                    # элемент-экземпляр потомка родительского класса)
                    if self._replacement:
                        item_value = self._replacement
                        self._replacement = False
                    new_value.append(item_value)
                else:
                    self._field_errors.append(ListValidationError(
                        value_repr=get_value_repr(item_value),
                        value_type=type(item_value), item_index=i,
                        annotation=annotation, exception=None
                    ))
                    return False

            # Все элементы списка value валидные.
            self._replacement = new_value
            return True
        else:
            # Значение поля - не список, а это ошибка валидации
            self._field_errors.append(BasicValidationError(
                value_repr=get_value_repr(value), value_type=type(value),
                annotation=annotation, exception=None
            ))
            return False

    def _is_literal_instance(self, value: Any, annotation: type) -> bool:
        """
            Валидация на алиас Literal.

            Проверяет является ли value одним из annotation.__args__
        """
        result = value in annotation.__args__

        if not result:
            self._field_errors.append(LiteralValidationError(
                value_repr=get_value_repr(value), value_type=type(value),
                annotation=annotation, exception=None
            ))

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


# ----------------------------------------------------------------------------


if __name__ == "__main__":

    print(get_value_repr(123456789012345678901234))

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
