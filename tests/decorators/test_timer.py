#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions.decorators.constants import TIMER_TRIGGER
from azure.functions.decorators.core import BindingDirection, DataType
from azure.functions.decorators.timer import TimerTrigger


class TestTimer(unittest.TestCase):
    def test_timer_trigger_valid_creation(self):
        trigger = TimerTrigger(name="req",
                               schedule="dummy_schedule",
                               data_type=DataType.UNDEFINED,
                               run_on_startup=False,
                               use_monitor=False,
                               dummy_field="dummy")

        self.assertEqual(trigger.get_binding_name(), "timerTrigger")
        self.assertEqual(trigger.get_dict_repr(), {
            "type": TIMER_TRIGGER,
            "direction": BindingDirection.IN,
            'dummyField': 'dummy',
            "name": "req",
            "dataType": DataType.UNDEFINED,
            "schedule": "dummy_schedule",
            "runOnStartup": False,
            "useMonitor": False
        })
