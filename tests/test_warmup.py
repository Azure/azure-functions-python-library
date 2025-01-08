# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest

import azure.functions as func
import azure.functions.warmup as warmup

from azure.functions.meta import Datum


class TestWarmup(unittest.TestCase):
    def test_warmup_decode(self):
        # given
        datum: Datum = Datum(value='''''', type='json')

        # when
        warmup_context: func.WarmUpContext = \
            warmup.WarmUpTriggerConverter.decode(datum, trigger_metadata={})

        # then
        self.assertTrue(isinstance(warmup_context, func.WarmUpContext))

    def test_warmup_input_type(self):
        check_input_type = (
            warmup.WarmUpTriggerConverter.check_input_type_annotation
        )
        self.assertTrue(check_input_type(func.WarmUpContext))
        self.assertFalse(check_input_type(str))
