#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.constants import RETRY_POLICY
from azure.functions.decorators.core import Setting


class RetryPolicy(Setting):

    def __init__(self,
                 strategy: str,
                 max_retry_count: str,
                 delay_interval: Optional[str],
                 minimum_interval: Optional[str],
                 maximum_interval: Optional[str],
                 **kwargs):
        self.strategy = strategy
        self.max_retry_count = max_retry_count
        self.delay_interval = delay_interval
        self.minimum_interval = minimum_interval
        self.maximum_interval = maximum_interval
        super().__init__(setting_type=RETRY_POLICY)

    def get_value(self, name: str) -> Optional[str]:
        return self.get_dict_repr().get(name)
