#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional, Dict

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
                 data_type: DataType,
                 document_id: Optional[str] = None,
                 sql_query: Optional[str] = None,
                 partition_key: Optional[str] = None):
        self.database_name = database_name
        self.collection_name = collection_name
        self.connection_string_setting = connection_string_setting
        self.partition_key = partition_key
        self.document_id = document_id
        self.sql_query = sql_query
        super().__init__(name=name, data_type=data_type)

    def get_dict_repr(self) -> Dict:
        return {
            "type": self.type,
            "direction": self.direction,
            "name": self.name,
            "dataType": self.data_type,
            "databaseName": self.database_name,
            "collectionName": self.collection_name,
            "connectionStringSetting": self.connection_string_setting,
            "id": self.document_id,
            "sqlQuery": self.sql_query,
            "partitionKey": self.partition_key
        }


class CosmosDBOutput(OutputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return COSMOS_DB

    def __init__(self,
                 name: str,
                 database_name: str,
                 collection_name: str,
                 connection_string_setting: str,
                 create_if_not_exists: bool,
                 collection_throughput: int,
                 use_multiple_write_loc: bool,
                 preferred_locations: Optional[str] = None,
                 partition_key: Optional[str] = None,
                 data_type: DataType = DataType.UNDEFINED):
        self.database_name = database_name
        self.collection_name = collection_name
        self.connection_string_setting = connection_string_setting
        self.create_if_not_exists = create_if_not_exists
        self.partition_key = partition_key
        self.collection_throughput = collection_throughput
        self.use_multiple_write_locations = use_multiple_write_loc
        self.preferred_locations = preferred_locations
        super().__init__(name=name, data_type=data_type)

    def get_dict_repr(self) -> Dict:
        return {
            "type": self.type,
            "direction": self.direction,
            "name": self.name,
            "dataType": self.data_type,
            "databaseName": self.database_name,
            "collectionName": self.collection_name,
            "connectionStringSetting": self.connection_string_setting,
            "createIfNotExists": self.create_if_not_exists,
            "partitionKey": self.partition_key,
            "collectionThroughput": self.collection_throughput,
            "useMultipleWriteLocations": self.use_multiple_write_locations,
            "preferredLocations": self.preferred_locations
        }


class CosmosDBTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return COSMOS_DB_TRIGGER

    def __init__(self,
                 name: str,
                 database_name: str,
                 collection_name: str,
                 connection_string_setting: str,
                 lease_coll_throughput: int,
                 checkpoint_interval: int,
                 checkpoint_document_count: int,
                 feed_poll_delay: int,
                 lease_renew_interval: int,
                 lease_acquire_interval: int,
                 lease_expiration_interval: int,
                 max_items_per_invocation: int,
                 start_from_beginning: bool,
                 create_lease_coll_if_unset: bool,
                 preferred_locations: str,
                 data_type: DataType,
                 lease_collection_name: Optional[str] = None,
                 lease_conn_str_setting: Optional[str] = None,
                 lease_database_name: Optional[str] = None,
                 lease_collection_prefix: Optional[str] = None,
                 ):
        self.lease_collection_name = lease_collection_name
        self.lease_connection_string_setting = lease_conn_str_setting
        self.lease_database_name = lease_database_name
        self.create_lease_collection_if_not_exists = \
            create_lease_coll_if_unset
        self.leases_collection_throughput = lease_coll_throughput
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

    def get_dict_repr(self) -> Dict:
        return {
            "type": self.type,
            "name": self.name,
            "direction": self.direction,
            "dataType": self.data_type,
            "leaseCollectionName": self.lease_collection_name,
            "leaseConnectionStringSetting":
                self.lease_connection_string_setting,
            "leaseDatabaseName": self.lease_database_name,
            "createLeaseCollectionIfNotExists":
                self.create_lease_collection_if_not_exists,
            "leasesCollectionThroughput": self.leases_collection_throughput,
            "leaseCollectionPrefix": self.lease_collection_prefix,
            "checkpointInterval": self.checkpoint_interval,
            "checkpointDocumentCount": self.checkpoint_document_count,
            "feedPollDelay": self.feed_poll_delay,
            "leaseRenewInterval": self.lease_renew_interval,
            "leaseAcquireInterval": self.lease_acquire_interval,
            "leaseExpirationInterval": self.lease_expiration_interval,
            "maxItemsPerInvocation": self.max_items_per_invocation,
            "startFromBeginning": self.start_from_beginning,
            "preferredLocations": self.preferred_locations,
            "connectionStringSetting": self.connection_string_setting,
            "databaseName": self.database_name,
            "collectionName": self.collection_name
        }
