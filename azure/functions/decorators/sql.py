#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.constants import SQL, SQL_TRIGGER
from azure.functions.decorators.core import DataType, InputBinding, \
    OutputBinding, Trigger

class SqlInput(InputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return SQL

    def __init__(self,
                name: str,
                commandText: str,
                connectionStringSetting: str,
                commandType: Optional[str] = 'Text',
                parameters: Optional[str] = None,
                data_type: Optional[DataType] = None,
                **kwargs):
        self.commandText = commandText
        self.connectionStringSetting = connectionStringSetting
        self.commandType = commandType
        self.parameters = parameters
        super().__init__(name=name, data_type=data_type)


class SqlOutput(OutputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return SQL

    def __init__(self,
                name: str,
                commandText: str,
                connectionStringSetting: str,
                data_type: Optional[DataType] = None,
                **kwargs):
        self.commandText = commandText
        self.connectionStringSetting = connectionStringSetting
        super().__init__(name=name, data_type=data_type)

class SqlTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return SQL_TRIGGER

    def __init__(self,
                name: str,
                tableName: str,
                connectionStringSetting: str,
                data_type: Optional[DataType] = None,
                **kwargs):
        self.tableName = tableName
        self.connectionStringSetting = connectionStringSetting
        super().__init__(name=name, data_type=data_type)