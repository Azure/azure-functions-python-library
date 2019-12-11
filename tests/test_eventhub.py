from typing import List
import unittest

import azure.functions as func
import azure.functions.eventhub as azf_eh


class TestEventHub(unittest.TestCase):
    def test_eventhub_input_type(self):
        check_input_type = (
            azf_eh.EventHubConverter.check_input_type_annotation
        )
        self.assertTrue(check_input_type(func.EventHubEvent))
        self.assertTrue(check_input_type(List[func.EventHubEvent]))
        self.assertFalse(check_input_type(str))
        self.assertFalse(check_input_type(bytes))
        self.assertFalse(check_input_type(List[str]))

    def test_eventhub_output_type(self):
        check_output_type = (
            azf_eh.EventHubTriggerConverter.check_output_type_annotation
        )
        self.assertTrue(check_output_type(bytes))
        self.assertTrue(check_output_type(str))
        self.assertTrue(check_output_type(List[str]))
        self.assertFalse(check_output_type(func.EventHubEvent))
        self.assertFalse(check_output_type(List[bytes]))
        self.assertFalse(check_output_type(List[func.EventHubEvent]))
