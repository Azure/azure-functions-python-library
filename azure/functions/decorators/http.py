# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from typing import Optional, Tuple

from azure.functions.decorators.core import AuthLevel, Trigger, OutputBinding, \
    StringifyEnum, DataType


class HttpMethod(StringifyEnum):
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"


class HttpTrigger(Trigger):
    @staticmethod
    def get_binding_name():
        return "httpTrigger"

    def __init__(self,
                 name,
                 data_type: Optional[DataType] = DataType.UNDEFINED,
                 methods: Optional[Tuple[HttpMethod]] = (),
                 auth_level: Optional[AuthLevel] = AuthLevel.ANONYMOUS,
                 route: Optional[str] = None) -> None:
        self.auth_level = auth_level
        self.route = route
        self.methods = methods
        super().__init__(name=name, data_type=data_type)

    def get_dict_repr(self):
        dict_repr = {
            "authLevel": str(self.auth_level),
            "type": self.type,
            "direction": self.direction,
            "name": self.name,
            "dataType": self.data_type,
            "route": self.route
        }
        if self.methods is not None:
            dict_repr["methods"] = [str(m) for m in self.methods]

        return dict_repr


class HttpOutput(OutputBinding):
    @staticmethod
    def get_binding_name():
        return "http"

    def __init__(self,
                 name: str,
                 data_type: Optional[DataType] = DataType.UNDEFINED) -> None:
        super().__init__(name=name, data_type=data_type)

    def get_dict_repr(self):
        return {
            "type": self.type,
            "direction": self.direction,
            "name": self.name,
            "dataType": self.data_type
        }
