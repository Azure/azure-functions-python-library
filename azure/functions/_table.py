#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import json
from typing import Optional

from . import _abc


class Table(_abc.Table):

    def __init__(self,
                 connection: str,
                 table_name: str,
                 row_key: Optional[str] = None,
                 partition_key: Optional[str] = None):
        self.__connection = connection
        self.__table_name = table_name
        self.__row_key = row_key
        self.__partition_key = partition_key

    def get_binding_name(self) -> str:
        return "table"

    @classmethod
    def from_json(cls, json_data: str) -> 'Table':
        """Create a Document from a JSON string."""
        return cls.from_dict(json.loads(json_data))

    @classmethod
    def from_dict(cls, dct: dict) -> 'Table':
        """Create a Document from a dict object."""
        return cls({k: v for k, v in dct.items()})

    def to_json(self) -> str:
        """Return the JSON representation of the document."""
        return json.dumps(dict(self))

    def to_dict(self) -> dict:
        """Return the document as a dict - directly using self would also work
        as Document is ``UserDict`` subclass and behave like dict"""
        return dict(self)

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
        return None

    @property
    def filter(self) -> str:
        return None
