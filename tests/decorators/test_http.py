#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions.decorators.constants import HTTP_TRIGGER, HTTP_OUTPUT
from azure.functions.decorators.core import BindingDirection, DataType, \
    AuthLevel
from azure.functions.decorators.http import HttpTrigger, HttpOutput, \
    HttpMethod


class TestHttp(unittest.TestCase):
    def test_http_method_enum(self):
        self.assertEqual([e for e in HttpMethod],
                         [HttpMethod.GET, HttpMethod.POST, HttpMethod.DELETE,
                          HttpMethod.HEAD, HttpMethod.PATCH, HttpMethod.PUT,
                          HttpMethod.OPTIONS])

    def test_http_trigger_valid_creation_with_methods(self):
        http_trigger = HttpTrigger(name='req',
                                   methods=[HttpMethod.GET, HttpMethod.POST],
                                   data_type=DataType.UNDEFINED,
                                   auth_level=AuthLevel.ANONYMOUS,
                                   route='dummy',
                                   dummy_field="dummy")

        self.assertEqual(http_trigger.get_binding_name(), HTTP_TRIGGER)
        self.assertEqual(http_trigger.get_dict_repr(), {
            "authLevel": AuthLevel.ANONYMOUS,
            "type": HTTP_TRIGGER,
            "direction": BindingDirection.IN,
            'dummyField': 'dummy',
            "name": 'req',
            "dataType": DataType.UNDEFINED,
            "route": 'dummy',
            "methods": [HttpMethod.GET, HttpMethod.POST]
        })

    def test_http_output_valid_creation(self):
        http_output = HttpOutput(name='req', data_type=DataType.UNDEFINED,
                                 dummy_field="dummy")

        self.assertEqual(http_output.get_binding_name(), HTTP_OUTPUT)
        self.assertEqual(http_output.get_dict_repr(), {
            "type": HTTP_OUTPUT,
            "direction": BindingDirection.OUT,
            'dummyField': 'dummy',
            "name": "req",
            "dataType": DataType.UNDEFINED,
        })
