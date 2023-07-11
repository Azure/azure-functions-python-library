#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions.decorators.retry_policy import RetryPolicy


class TestRetryPolicy(unittest.TestCase):

    def test_retry_policy_setting_creation(self):
        retry_policy = RetryPolicy(max_retry_count="1",
                                   strategy="fixed",
                                   delay_interval="5")

        self.assertEqual(retry_policy.get_setting_name(), "retry_policy")
        self.assertEqual(retry_policy.get_dict_repr(),
                         {'setting_name': 'retry_policy',
                          'strategy': 'fixed',
                          'max_retry_count': '1',
                          'delay_interval': '5'})

        retry_policy = RetryPolicy(max_retry_count="1",
                                   strategy="exponential",
                                   minimum_interval="5",
                                   maximum_interval="10")
        self.assertEqual(retry_policy.get_dict_repr(),
                         {'setting_name': 'retry_policy',
                          'strategy': 'exponential',
                          'minimum_interval': '5',
                          'max_retry_count': '1',
                          'maximum_interval': '10'})
