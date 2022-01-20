# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from azure.functions.decorators.core import AuthLevel, Trigger, OutputBinding, \
    StringifyEnum


class HttpMethod(StringifyEnum):
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"


class HttpTrigger(Trigger):
    @staticmethod
    def get_binding_name():
        return "httpTrigger"

    def __init__(self, name, methods=None,
                 auth_level: AuthLevel = AuthLevel.ANONYMOUS,
                 route='/api') -> None:
        self.auth_level = auth_level
        self.route = route
        self.methods = methods
        super().__init__(name=name)

    def get_dict_repr(self):
        dict_repr = {
            "authLevel": str(self.auth_level),
            "type": self.get_binding_name(),
            "direction": self.get_binding_direction(),
            "name": self.name
        }
        if self.methods is not None:
            dict_repr["methods"] = [str(m) for m in self.methods]

        return dict_repr


class Http(OutputBinding):
    @staticmethod
    def get_binding_name():
        return "http"

    def __init__(self, name="$return") -> None:
        super().__init__(name=name)

    def get_dict_repr(self):
        return {
            "type": self.get_binding_name(),
            "direction": self.get_binding_direction(),
            "name": self.name
        }
