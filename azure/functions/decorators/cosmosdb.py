#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional, Union

from azure.functions.decorators.constants import COSMOS_DB, COSMOS_DB_TRIGGER
from azure.functions.decorators.core import DataType, InputBinding, \
    OutputBinding, Trigger


class CosmosDBInput(InputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return COSMOS_DB

    def __init__(self,
                 name: str,
                 database_name: str,
                 collection_name: str,
                 connection_string_setting: str,
                 data_type: Optional[DataType] = None,
                 id: Optional[str] = None,
                 sql_query: Optional[str] = None,
                 partition_key: Optional[str] = None,
                 **kwargs):
        self.database_name = database_name
        self.collection_name = collection_name
        self.connection_string_setting = connection_string_setting
        self.partition_key = partition_key
        self.id = id
        self.sql_query = sql_query
        super().__init__(name=name, data_type=data_type)


class CosmosDBOutput(OutputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return COSMOS_DB

    def __init__(self,
                 name: str,
                 database_name: str,
                 collection_name: str,
                 connection_string_setting: str,
                 create_if_not_exists: Optional[bool] = None,
                 collection_throughput: Optional[int] = None,
                 use_multiple_write_locations: Optional[bool] = None,
                 preferred_locations: Optional[str] = None,
                 partition_key: Optional[str] = None,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.database_name = database_name
        self.collection_name = collection_name
        self.connection_string_setting = connection_string_setting
        self.create_if_not_exists = create_if_not_exists
        self.partition_key = partition_key
        self.collection_throughput = collection_throughput
        self.use_multiple_write_locations = use_multiple_write_locations
        self.preferred_locations = preferred_locations
        super().__init__(name=name, data_type=data_type)


class CosmosDBTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return COSMOS_DB_TRIGGER

    def __init__(self,
                 name: str,
                 database_name: str,
                 collection_name: str,
                 connection_string_setting: str,
                 leases_collection_throughput: Optional[int] = None,
                 checkpoint_interval: Optional[int] = None,
                 checkpoint_document_count: Optional[int] = None,
                 feed_poll_delay: Optional[int] = None,
                 lease_renew_interval: Optional[int] = None,
                 lease_acquire_interval: Optional[int] = None,
                 lease_expiration_interval: Optional[int] = None,
                 max_items_per_invocation: Optional[int] = None,
                 start_from_beginning: Optional[bool] = None,
                 create_lease_collection_if_not_exists: Optional[bool] = None,
                 preferred_locations: Optional[str] = None,
                 data_type: Optional[Union[DataType]] = None,
                 lease_collection_name: Optional[str] = None,
                 lease_connection_string_setting: Optional[str] = None,
                 lease_database_name: Optional[str] = None,
                 lease_collection_prefix: Optional[str] = None,
                 **kwargs):
        self.lease_collection_name = lease_collection_name
        self.lease_connection_string_setting = lease_connection_string_setting
        self.lease_database_name = lease_database_name
        self.create_lease_collection_if_not_exists = \
            create_lease_collection_if_not_exists
        self.leases_collection_throughput = leases_collection_throughput
        self.lease_collection_prefix = lease_collection_prefix
        self.checkpoint_interval = checkpoint_interval
        self.checkpoint_document_count = checkpoint_document_count
        self.feed_poll_delay = feed_poll_delay
        self.lease_renew_interval = lease_renew_interval
        self.lease_acquire_interval = lease_acquire_interval
        self.lease_expiration_interval = lease_expiration_interval
        self.max_items_per_invocation = max_items_per_invocation
        self.start_from_beginning = start_from_beginning
        self.preferred_locations = preferred_locations
        self.connection_string_setting = connection_string_setting
        self.database_name = database_name
        self.collection_name = collection_name
        super().__init__(name=name, data_type=data_type)
