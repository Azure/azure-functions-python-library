#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import json

from azure.functions.decorators.utils import CustomJsonEncoder


def assert_json(self, func, expected_dict):
    self.assertEqual(json.dumps(json.loads(str(func)), sort_keys=True,
                                cls=CustomJsonEncoder),
                     json.dumps(expected_dict, sort_keys=True,
                                cls=CustomJsonEncoder))
