#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions.decorators.function_name import FunctionName


class TestFunctionName(unittest.TestCase):

    def test_retry_policy_setting_creation(self):
        function_name = FunctionName(name="TestFunctionName")

        self.assertEqual(function_name.get_setting_type(), "function_name")
        self.assertEqual(function_name.get_dict_repr(),
                         {'setting_type': 'function_name',
                          'name': 'TestFunctionName'})