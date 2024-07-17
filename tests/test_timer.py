# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
import unittest

import azure.functions.timer as timer
from azure.functions.meta import Datum


class TestTimer(unittest.TestCase):
    def test_timer_decode(self):
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
        timer_request: timer.TimerRequest = \
            timer.TimerRequestConverter.decode(datum, trigger_metadata={})

        # then
        self.assertEqual(timer_request.schedule, data_dict["Schedule"])
        self.assertEqual(timer_request.schedule_status,
                         data_dict["ScheduleStatus"])
        self.assertEqual(timer_request.past_due, data_dict["IsPastDue"])

    def test_timer_initialize_without_args(self):
        # given
        past_due = False
        schedule_status = {}
        schedule = {}

        # when
        test_timer = timer.TimerRequest()

        # then
        self.assertEqual(past_due, test_timer.past_due)
        self.assertEqual(schedule_status, test_timer.schedule_status)
        self.assertEqual(schedule, test_timer.schedule)

    def test_timer_initialize_empty_dicts(self):
        # given
        past_due = False

        # when
        test_timer = timer.TimerRequest()

        # then
        self.assertEqual(past_due, test_timer.past_due)
        self.assertEqual({}, test_timer.schedule_status)
        self.assertEqual({}, test_timer.schedule)

    def test_timer_no_implementation_exception(self):
        # given
        datum: Datum = Datum(value="test", type='string')
        is_exception_raised = False

        # when
        try:
            timer.TimerRequestConverter.decode(datum, trigger_metadata={})
        except NotImplementedError:
            is_exception_raised = True

        # then
        self.assertTrue(is_exception_raised)

    def test_timer_input_type(self):
        check_input_type = (
            timer.TimerRequestConverter.check_input_type_annotation
        )
        self.assertTrue(check_input_type(timer.TimerRequest))
        self.assertFalse(check_input_type(str))
