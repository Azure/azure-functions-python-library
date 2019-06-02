import abc
import collections.abc
import datetime
import json
import re
import typing

from ._thirdparty import typing_inspect


def is_iterable_type_annotation(annotation: object, pytype: object) -> bool:
    is_iterable_anno = (
        typing_inspect.is_generic_type(annotation) and
        issubclass(typing_inspect.get_origin(annotation),
                   collections.abc.Iterable)
    )

    if not is_iterable_anno:
        return False

    args = typing_inspect.get_args(annotation)
    if not args:
        return False

    if isinstance(pytype, tuple):
        return any(isinstance(t, type) and issubclass(t, arg)
                   for t in pytype for arg in args)
    else:
        return any(isinstance(pytype, type) and issubclass(pytype, arg)
                   for arg in args)


class Datum:
    def __init__(self, value, type):
        self.value = value
        self.type = type

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        return self.value == other.value and self.type == other.type

    def __hash__(self):
        return hash((type(self), (self.value, self.type)))

    def __repr__(self):
        val_repr = repr(self.value)
        if len(val_repr) > 10:
            val_repr = val_repr[:10] + '...'
        return '<Datum {} {}>'.format(self.type, val_repr)


class _ConverterMeta(abc.ABCMeta):

    _bindings: typing.Mapping[str, type] = {}

    def __new__(mcls, name, bases, dct, *,
                binding: typing.Optional[str],
                trigger: typing.Optional[str]=None):
        cls = super().__new__(mcls, name, bases, dct)
        cls._trigger = trigger
        if binding is None:
            return cls

        if binding in mcls._bindings:
            raise RuntimeError(
                f'cannot register a converter for {binding!r} binding: '
                f'another converter for this binding has already been '
                f'registered')
        mcls._bindings[binding] = cls
        if trigger is not None:
            mcls._bindings[trigger] = cls

        return cls

    @classmethod
    def get(cls, binding_name):
        return cls._bindings.get(binding_name)

    def has_trigger_support(cls) -> bool:
        return cls._trigger is not None


class _BaseConverter(metaclass=_ConverterMeta, binding=None):

    @classmethod
    def _decode_typed_data(
            cls, data: Datum, *,
            python_type: typing.Union[type, typing.Tuple[type, ...]],
            context: str='data') -> typing.Any:
        if data is None:
            return None

        data_type = data.type
        if data_type == 'json':
            result = json.loads(data.value)

        elif data_type == 'string':
            result = data.value

        elif data_type == 'int':
            result = data.value

        elif data_type == 'double':
            result = data.value

        else:
            raise ValueError(
                f'unsupported type of {context}: {data_type}')

        if not isinstance(result, python_type):
            if isinstance(python_type, (tuple, list, dict)):
                raise ValueError(
                    f'unexpected value type in {context}: '
                    f'{type(result).__name__}, expected one of: '
                    f'{", ".join(t.__name__ for t in python_type)}')
            else:
                try:
                    # Try coercing into the requested type
                    result = python_type(result)
                except (TypeError, ValueError) as e:
                    raise ValueError(
                        f'cannot convert value of {context} into '
                        f'{python_type.__name__}: {e}') from None

        return result

    @classmethod
    def _decode_trigger_metadata_field(
            cls, trigger_metadata: typing.Mapping[str, Datum],
            field: str, *,
            python_type: typing.Union[type, typing.Tuple[type, ...]]) \
            -> typing.Any:
        data = trigger_metadata.get(field)
        if data is None:
            return None
        else:
            return cls._decode_typed_data(
                data, python_type=python_type,
                context=f'field {field!r} in trigger metadata')

    @classmethod
    def _parse_datetime_metadata(
            cls, trigger_metadata: typing.Mapping[str, Datum],
            field: str) -> typing.Optional[datetime.datetime]:

        datetime_str = cls._decode_trigger_metadata_field(
            trigger_metadata, field, python_type=str)

        if datetime_str is None:
            return None
        else:
            return cls._parse_datetime(datetime_str)

    @classmethod
    def _parse_timedelta_metadata(
            cls, trigger_metadata: typing.Mapping[str, Datum],
            field: str) -> typing.Optional[datetime.timedelta]:

        timedelta_str = cls._decode_trigger_metadata_field(
            trigger_metadata, field, python_type=str)

        if timedelta_str is None:
            return None
        else:
            return cls._parse_timedelta(timedelta_str)

    @classmethod
    def _parse_datetime(
            cls, datetime_str: str) -> datetime.datetime:
        # UTC ISO 8601 assumed
        formats = [
            '%Y-%m-%dT%H:%M:%S+00:00',
            '%Y-%m-%dT%H:%M:%S.%f+00:00',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ',
        ]
        dt = None

        too_fractional = re.match(r'.*\.\d{6}(\d+)Z', datetime_str)
        if too_fractional:
            # The supplied value contains seven digits in the
            # fractional second part, whereas Python expects
            # a maxium of six, so strip it.
            # https://github.com/Azure/azure-functions-python-worker/issues/269
            extra_digits = len(too_fractional.group(1))
            datetime_str = datetime_str[:-extra_digits - 1] + 'Z'

        for fmt in formats:
            try:
                dt = datetime.datetime.strptime(datetime_str, fmt)
            except ValueError as e:
                last_error = e

        if dt is None:
            raise last_error

        return dt.replace(tzinfo=datetime.timezone.utc)

    @classmethod
    def _parse_timedelta(
            cls, timedelta_str: str) -> datetime.timedelta:
        raise NotImplementedError


class InConverter(_BaseConverter, binding=None):

    @abc.abstractclassmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        pass

    @abc.abstractclassmethod
    def decode(cls, data: Datum, *, trigger_metadata) -> typing.Any:
        raise NotImplementedError


class OutConverter(_BaseConverter, binding=None):

    @abc.abstractclassmethod
    def check_output_type_annotation(cls, pytype: type) -> bool:
        pass

    @abc.abstractclassmethod
    def encode(cls, obj: typing.Any, *,
               expeced_type: typing.Optional[type]) -> Datum:
        raise NotImplementedError


def get_binding_registry():
    return _ConverterMeta
