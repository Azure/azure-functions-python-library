# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
import unittest

import azure.functions.timer as timer
from azure.functions.meta import Datum


class TestTimer(unittest.TestCase):
    def test_TimerRequestConverter_decode(self):
        # given
        data = '''{"Schedule":{"AdjustForDST":true},
                   "ScheduleStatus":{
                        "Last":"2022-03-28T15:40:00.0105419-05:00",
                        "Next":"2022-03-28T15:45:00-05:00",
                        "LastUpdated":"2022-03-28T15:40:00.0105419-05:00"},
                   "IsPastDue":false}'''
        datum: Datum = Datum(value=data, type='json')
        data_dict = json.loads(data)

        # when
        timerRequest: timer.TimerRequest = \
            timer.TimerRequestConverter.decode(datum, trigger_metadata={})

        # then
        self.assertEqual(timerRequest.schedule, data_dict["Schedule"])
        self.assertEqual(timerRequest.schedulestatus,
                         data_dict["ScheduleStatus"])
        self.assertEqual(timerRequest.past_due, data_dict["IsPastDue"])
