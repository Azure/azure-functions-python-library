#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.core import DataType, InputBinding, \
    OutputBinding, Trigger


class CosmosDBInput(InputBinding):
    @staticmethod
    def get_binding_name():
        return "cosmosDB"

    def __init__(self,
                 name: str,
                 database_name: str,
                 collection_name: str,
                 connection_string_setting: str,
                 document_id: Optional[str] = None,
                 sql_query: Optional[str] = None,
                 partitions: Optional[str] = None,
                 data_type: Optional[DataType] = DataType.UNDEFINED):
        self.database_name = database_name
        self.collection_name = collection_name
        self.connection_string_setting = connection_string_setting
        self.partitions = partitions
        self.document_id = document_id
        self.sql_query = sql_query
        super().__init__(name=name, data_type=data_type)

    def get_dict_repr(self):
        return {
            "type": self.type,
            "direction": self.direction,
            "name": self.name,
            "dataType": self.data_type,
            "databaseName": self.database_name,
            "collectionName": self.collection_name,
            "collectionStringSetting": self.connection_string_setting,
            "document_id": self.document_id,
            "sqlQuery": self.sql_query,
            "partitions": self.partitions
        }


class CosmosDBOutput(OutputBinding):
    @staticmethod
    def get_binding_name():
        return "cosmosDB"

    def __init__(self,
                 name: str,
                 database_name: str,
                 collection_name: str,
                 connection_string_setting: str,
                 create_if_not_exists: Optional[bool] = False,
                 partition_key: Optional[str] = None,
                 collection_throughput: Optional[int] = -1,
                 use_multiple_write_locations: Optional[bool] = False,
                 preferred_locations: Optional[str] = None,
                 data_type: Optional[DataType] = DataType.UNDEFINED):
        self.database_name = database_name
        self.collection_name = collection_name
        self.connection_string_setting = connection_string_setting
        self.create_if_not_exists = create_if_not_exists
        self.partition_key = partition_key
        self.collection_throughput = collection_throughput
        self.use_multiple_write_locations = use_multiple_write_locations
        self.preferred_locations = preferred_locations
        super().__init__(name=name, data_type=data_type)

    def get_dict_repr(self):
        return {
            "type": self.type,
            "direction": self.direction,
            "name": self.name,
            "dataType": self.data_type,
            "databaseName": self.database_name,
            "collectionName": self.collection_name,
            "connectionStringSetting": self.connection_string_setting,
            "createIfNotExists": self.connection_string_setting,
            "partitionKey": self.partition_key,
            "collectionThroughput": self.collection_throughput,
            "useMultipleWriteLocations": self.use_multiple_write_locations,
            "preferredLocations": self.preferred_locations
        }


class CosmosDBTrigger(Trigger):
    def __init__(self,
                 name: str,
                 database_name: str,
                 collection_name: str,
                 connection_string_setting: str,
                 lease_collection_name: Optional[str] = None,
                 lease_connection_string_setting: Optional[str] = None,
                 lease_database_name: Optional[str] = None,
                 create_lease_collection_if_not_exists: Optional[bool] = False,
                 leases_collection_throughput: Optional[int] = -1,
                 lease_collection_prefix: Optional[str] = None,
                 checkpoint_interval: Optional[int] = -1,
                 checkpoint_document_count: Optional[int] = -1,
                 feed_poll_delay: Optional[int] = 5000,
                 lease_renew_interval: Optional[int] = 17000,
                 lease_acquire_interval: Optional[int] = 13000,
                 lease_expiration_interval: Optional[int] = 60000,
                 max_items_per_invocation: Optional[int] = -1,
                 start_from_beginning: Optional[bool] = False,
                 preferred_locations: Optional[str] = None,
                 data_type: Optional[DataType] = DataType.UNDEFINED):
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

    @staticmethod
    def get_binding_name():
        return "cosmosDBTrigger"

    def get_dict_repr(self):
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
