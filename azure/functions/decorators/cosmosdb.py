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
                 data_type: DataType,
                 document_id: Optional[str] = None,
                 sql_query: Optional[str] = None,
                 partition_key: Optional[str] = None):
        self._database_name = database_name
        self._collection_name = collection_name
        self._connection_string_setting = connection_string_setting
        self._partition_key = partition_key
        self._document_id = document_id
        self._sql_query = sql_query
        super().__init__(name=name, data_type=data_type)

    @property
    def database_name(self):
        return self._database_name

    @property
    def collection_name(self):
        return self._collection_name

    @property
    def connection_string_setting(self):
        return self._connection_string_setting

    @property
    def document_id(self):
        return self._document_id

    @property
    def sql_query(self):
        return self._sql_query

    @property
    def partition_key(self):
        return self._partition_key

    def get_dict_repr(self):
        return {
            "type": self.type,
            "direction": self._direction.name,
            "name": self.name,
            "dataType": self._data_type.name,
            "databaseName": self.database_name,
            "collectionName": self.collection_name,
            "collectionStringSetting": self.connection_string_setting,
            "document_id": self.document_id,
            "sqlQuery": self.sql_query,
            "partitionKey": self.partition_key
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
                 create_if_not_exists: bool,
                 collection_throughput: int,
                 use_multiple_write_loc: bool,
                 preferred_locations: Optional[str] = None,
                 partition_key: Optional[str] = None,
                 data_type: DataType = DataType.UNDEFINED):
        self._database_name = database_name
        self._collection_name = collection_name
        self._connection_string_setting = connection_string_setting
        self._create_if_not_exists = create_if_not_exists
        self._partition_key = partition_key
        self._collection_throughput = collection_throughput
        self._use_multiple_write_locations = use_multiple_write_loc
        self._preferred_locations = preferred_locations
        super().__init__(name=name, data_type=data_type)

    @property
    def database_name(self):
        return self._database_name

    @property
    def collection_name(self):
        return self._collection_name

    @property
    def connection_string_setting(self):
        return self._connection_string_setting

    @property
    def create_if_not_exists(self):
        return self._create_if_not_exists

    @property
    def partition_key(self):
        return self._partition_key

    @property
    def collection_throughput(self):
        return self._collection_throughput

    @property
    def use_multiple_write_locations(self):
        return self._use_multiple_write_locations

    @property
    def preferred_locations(self):
        return self._preferred_locations

    def get_dict_repr(self):
        return {
            "type": self.type,
            "direction": self._direction.name,
            "name": self.name,
            "dataType": self._data_type.name,
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
    def get_binding_name():
        return "cosmosDBTrigger"

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
        self._lease_collection_name = lease_collection_name
        self._lease_connection_string_setting = lease_conn_str_setting
        self._lease_database_name = lease_database_name
        self._create_lease_collection_if_not_exists = \
            create_lease_coll_if_unset
        self._leases_collection_throughput = lease_coll_throughput
        self._lease_collection_prefix = lease_collection_prefix
        self._checkpoint_interval = checkpoint_interval
        self._checkpoint_document_count = checkpoint_document_count
        self._feed_poll_delay = feed_poll_delay
        self._lease_renew_interval = lease_renew_interval
        self._lease_acquire_interval = lease_acquire_interval
        self._lease_expiration_interval = lease_expiration_interval
        self._max_items_per_invocation = max_items_per_invocation
        self._start_from_beginning = start_from_beginning
        self._preferred_locations = preferred_locations
        self._connection_string_setting = connection_string_setting
        self._database_name = database_name
        self._collection_name = collection_name
        super().__init__(name=name, data_type=data_type)

    @property
    def lease_collection_name(self):
        return self._lease_collection_name

    @property
    def lease_connection_string_setting(self):
        return self._lease_connection_string_setting

    @property
    def lease_database_name(self):
        return self._lease_database_name

    @property
    def create_lease_collection_if_not_exists(self):
        return self._create_lease_collection_if_not_exists

    @property
    def leases_collection_throughput(self):
        return self._leases_collection_throughput

    @property
    def lease_collection_prefix(self):
        return self._lease_collection_prefix

    @property
    def checkpoint_interval(self):
        return self._checkpoint_interval

    @property
    def checkpoint_document_count(self):
        return self._checkpoint_document_count

    @property
    def feed_poll_delay(self):
        return self._feed_poll_delay

    @property
    def lease_renew_interval(self):
        return self._lease_renew_interval

    @property
    def lease_acquire_interval(self):
        return self._lease_acquire_interval

    @property
    def lease_expiration_interval(self):
        return self._lease_expiration_interval

    @property
    def max_items_per_invocation(self):
        return self._max_items_per_invocation

    @property
    def start_from_beginning(self):
        return self._start_from_beginning

    @property
    def preferred_locations(self):
        return self._preferred_locations

    @property
    def connection_string_setting(self):
        return self._connection_string_setting

    @property
    def database_name(self):
        return self._database_name

    @property
    def collection_name(self):
        return self._collection_name

    def get_dict_repr(self):
        return {
            "type": self.type,
            "name": self.name,
            "direction": self._direction.name,
            "dataType": self._data_type.name,
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
