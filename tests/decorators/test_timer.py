#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions import DataType
from azure.functions.decorators.core import BindingDirection
from azure.functions.decorators.timer import TimerTrigger


class TestTimer(unittest.TestCase):
    def test_timer_trigger_valid_creation(self):
        trigger = TimerTrigger(name="req",
                               schedule="dummy_schedule",
                               data_type=DataType.UNDEFINED,
                               run_on_startup=False,
                               use_monitor=False)

        self.assertEqual(trigger.get_binding_name(), "timerTrigger")
        self.assertEqual(trigger.get_dict_repr(), {
            "type": "timerTrigger",
            "direction": str(BindingDirection.IN),
            "name": "req",
            "dataType": str(DataType.UNDEFINED),
            "schedule": "dummy_schedule",
            "runOnStartup": False,
            "useMonitor": False
        })
