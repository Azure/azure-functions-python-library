#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import datetime
import json
from typing import Dict, Any, List, Union, Optional, Mapping, cast

from azure.functions import _table as azf_table

from . import meta


class Table(azf_table.Table):

    def __init__(self,
                 connection: str,
                 table_name: str,
                 row_key: Optional[str] = None,
                 partition_key: Optional[str] = None,
                 take: Optional[int] = None,
                 filter: Optional[str] = None):
        self.__connection = connection
        self.__table_name = table_name
        self.__row_key = row_key
        self.__partition_key = partition_key
        self.__take = take
        self.__filter = filter

    def get_binding_name(self) -> str:
        return "table"

    @property
    def connection(self) -> str:
        return self.__connection

    @property
    def table_name(self) -> str:
        return self.__table_name

    @property
    def row_key(self) -> str:
        return self.__row_key

    @property
    def partition_key(self) -> str:
        return self.__partition_key

    @property
    def take(self) -> str:
        return self.__take

    @property
    def filter(self) -> str:
        return self.__filter

class TableConverter(meta.InConverter,
                    meta.OutConverter,
                    binding='table'):
    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (azf_table.Table, bytes, str))

    @classmethod
    def check_output_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (str, bytes, bytearray, azf_table.Table))

    @classmethod
    def encode(cls, obj: Any, *,
               expected_type: Optional[type]) -> meta.Datum:
        if isinstance(obj, str):
            return meta.Datum(type='string', value=obj)

        elif isinstance(obj, (bytes, bytearray)):
            return meta.Datum(type='bytes', value=bytes(obj))

        else:
            raise NotImplementedError

    @classmethod
    def decode(cls, data: meta.Datum, *, trigger_metadata) -> Any:
        if data is None or data.type is None:
            return None

        data_type = data.type

        if data_type == 'string':
            data = data.value.encode('utf-8')
        elif data_type == 'bytes':
            data = data.value
        elif data_type == 'json':
            data = json.loads(data.value)
        else:
            raise ValueError(
                f'unexpected type of data received for the "table" binding '
                f': {data_type!r}'
            )

        return Table(
                connection=cls._decode_trigger_metadata_field(
                    trigger_metadata, 'connection', python_type=str),
                table_name=cls._decode_trigger_metadata_field(
                    trigger_metadata, 'table_name', python_type=str),
                row_key=cls._decode_trigger_metadata_field(
                    trigger_metadata, 'row_key', python_type=str),
                partition_key=cls._decode_trigger_metadata_field(
                    trigger_metadata, 'partition_key', python_type=str),
                take=cls._decode_trigger_metadata_field(
                    trigger_metadata, 'take', python_type=str),
                filter=cls._decode_trigger_metadata_field(
                    trigger_metadata, 'filter', python_type=str)
            )