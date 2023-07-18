# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest
import azure.functions.warmup as warmup

from azure.functions.meta import Datum


class TestWarmup(unittest.TestCase):
    def test_warmup_decode(self):
        # given
        datum: Datum = Datum(value='''''', type='json')

        # when
        warmup_context: warmup.WarmUpContext = \
            warmup.WarmUpTriggerConverter.decode(datum, trigger_metadata={})

        # then
        self.assertTrue(isinstance(warmup_context, warmup.WarmUpContext))

    def test_warmup_input_type(self):
        check_input_type = (
            warmup.WarmUpTriggerConverter.check_input_type_annotation
        )
        self.assertTrue(check_input_type(warmup.WarmUpContext))
        self.assertFalse(check_input_type(str))
