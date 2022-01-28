#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.

from enum import Enum
from typing import Optional, Tuple

from azure.functions import DataType
from azure.functions.decorators.servicebus import AccessRights, Cardinality


class HttpMethod(Enum):
    """This Enum defines all the supported Http methods.
    """
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"


class AuthLevel(Enum):
    FUNCTION = "function"
    ANONYMOUS = "anonymous"
    ADMIN = "admin"


class FunctionsApp(object):
    def function_name(self, name: str):
        pass

    def route(self,
              trigger_arg_name: str = 'req',
              binding_arg_name: str = '$return',
              trigger_arg_data_type: DataType = DataType.UNDEFINED,
              output_arg_data_type: DataType = DataType.UNDEFINED,
              methods: Tuple[HttpMethod] = (HttpMethod.GET, HttpMethod.POST),
              auth_level: Optional[AuthLevel] = None,
              route: Optional[str] = None):
        pass

    def schedule(self,
                 name: str,
                 schedule: str,
                 run_on_startup: bool = False,
                 use_monitor: bool = False,
                 data_type: DataType = DataType.UNDEFINED):
        pass

    def on_service_bus_queue_change(self,
                                    name: str,
                                    connection: str,
                                    queue_name: str,
                                    data_type: DataType = DataType.UNDEFINED,
                                    access_rights: AccessRights =
                                    AccessRights.MANAGE,
                                    is_sessions_enabled: bool = False,
                                    cardinality: Cardinality = Cardinality.ONE):
        pass

    def on_service_bus_topic_change(self,
                                    name: str,
                                    connection: str,
                                    topic_name: str,
                                    subscription_name: str,
                                    data_type: DataType = DataType.UNDEFINED,
                                    access_rights: AccessRights =
                                    AccessRights.MANAGE,
                                    is_sessions_enabled: bool = False,
                                    cardinality: Cardinality = Cardinality.ONE):
        pass

    def write_service_bus_queue(self,
                                name: str,
                                connection: str,
                                queue_name: str,
                                data_type: DataType = DataType.UNDEFINED,
                                access_rights: AccessRights =
                                AccessRights.MANAGE):
        pass

    def write_service_bus_topic(self,
                                name: str,
                                connection: str,
                                topic_name: str,
                                subscription_name: str,
                                data_type: DataType = DataType.UNDEFINED,
                                access_rights: AccessRights =
                                AccessRights.MANAGE):
        pass

    def on_queue_change(self,
                        name: str,
                        queue_name: str,
                        connection: str,
                        data_type: DataType = DataType.UNDEFINED):
        pass

    def write_queue(self,
                    name: str,
                    queue_name: str,
                    connection: str,
                    data_type: DataType = DataType.UNDEFINED):
        pass

    def on_event_hub_message(self,
                             name: str,
                             connection: str,
                             event_hub_name: str,
                             data_type: DataType = DataType.UNDEFINED,
                             cardinality: Cardinality = Cardinality.MANY,
                             consumer_group: str = "$Default"):
        pass

    def write_event_hub_message(self,
                                name: str,
                                connection: str,
                                event_hub_name: str,
                                data_type: DataType =
                                DataType.UNDEFINED):
        pass

    def on_cosmos_db_update(self,
                            name: str,
                            database_name: str,
                            collection_name: str,
                            connection_string_setting: str,
                            lease_collection_name: Optional[str] = None,
                            lease_connection_string_setting: Optional[
                                str] = None,
                            lease_database_name: Optional[str] = None,
                            create_lease_collection_if_not_exists: bool = False,
                            leases_collection_throughput: int = -1,
                            lease_collection_prefix: Optional[str] = None,
                            checkpoint_interval: int = -1,
                            checkpoint_document_count: int = -1,
                            feed_poll_delay: int = 5000,
                            lease_renew_interval: int = 17000,
                            lease_acquire_interval: int = 13000,
                            lease_expiration_interval: int = 60000,
                            max_items_per_invocation: int = -1,
                            start_from_beginning: bool = False,
                            preferred_locations: Optional[str] = None,
                            data_type: DataType = DataType.UNDEFINED):
        pass

    def write_cosmos_db_documents(self,
                                  name: str,
                                  database_name: str,
                                  collection_name: str,
                                  connection_string_setting: str,
                                  create_if_not_exists: bool = False,
                                  partition_key: Optional[str] = None,
                                  collection_throughput: int = -1,
                                  use_multiple_write_locations: bool = False,
                                  preferred_locations: Optional[str] = None,
                                  data_type: DataType = DataType.UNDEFINED):
        pass

    def read_cosmos_db_documents(self,
                                 name: str,
                                 database_name: str,
                                 collection_name: str,
                                 connection_string_setting: str,
                                 document_id: Optional[str] = None,
                                 sql_query: Optional[str] = None,
                                 partitions: Optional[str] = None,
                                 data_type: DataType = DataType.UNDEFINED):
        pass
