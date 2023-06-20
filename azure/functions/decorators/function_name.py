#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.

from azure.functions.decorators.constants import FUNCTION_NAME
from azure.functions.decorators.core import Setting


class FunctionName(Setting):

    def __init__(self, name: str,
                 **kwargs):
        self.name = name
        super().__init__(setting_type=FUNCTION_NAME)
