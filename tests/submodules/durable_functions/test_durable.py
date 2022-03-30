# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest


class TestDurable(unittest.TestCase):
    def test_durable_functions_module_import(self):
        import azure.functions.durable as df

        self.assertEqual(df.__name__, 'azure.functions.durable')
