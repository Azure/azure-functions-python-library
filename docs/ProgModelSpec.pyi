#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.

from typing import Set, Optional
from enum import Enum

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

    def on_http_request(self,
                        name: str = 'req',
                        data_type: Optional[DataType] = DataType.UNDEFINED,
                        methods: Set[HttpMethod] =
                        (HttpMethod.GET, HttpMethod.POST),
                        auth_level: Optional[AuthLevel] = AuthLevel.ANONYMOUS,
                        route: Optional[str] = None):
        pass

    def write_http(self,
                   name: str = '$return',
                   data_type: Optional[DataType] = DataType.UNDEFINED):
        pass

    def route(self,
              trigger_arg_name: str = 'req',
              binding_arg_name: str = '$return',
              trigger_arg_data_type: Optional[DataType] = DataType.UNDEFINED,
              output_arg_data_type: Optional[DataType] = DataType.UNDEFINED,
              methods: Set[HttpMethod] = (HttpMethod.GET, HttpMethod.POST),
              auth_level: Optional[AuthLevel] = AuthLevel.ANONYMOUS,
              route: Optional[str] = None):
        pass

    def schedule(self,
                 name: str,
                 schedule: str,
                 run_on_startup: Optional[bool] = None,
                 use_monitor: Optional[bool] = None,
                 data_type: Optional[DataType] = DataType.UNDEFINED):
        pass

    def on_service_bus_queue_change(self,
                                    name: str,
                                    connection: str,
                                    queue_name: str,
                                    data_type: Optional[
                                        DataType] = DataType.UNDEFINED,
                                    access_rights: Optional[
                                        AccessRights] = AccessRights.MANAGE,
                                    is_sessions_enabled: Optional[bool] = False,
                                    cardinality: Optional[
                                        Cardinality] = Cardinality.ONE):
        pass

    def on_service_bus_topic_change(self,
                                    name: str,
                                    connection: str,
                                    topic_name: str,
                                    subscription_name: str,
                                    data_type: Optional[
                                        DataType] = DataType.UNDEFINED,
                                    access_rights: Optional[
                                        AccessRights] = AccessRights.MANAGE,
                                    is_sessions_enabled: Optional[bool] = False,
                                    cardinality: Optional[
                                        Cardinality] = Cardinality.ONE):
        pass

    def write_service_bus_queue(self,
                                name: str,
                                connection: str,
                                queue_name: str,
                                data_type: Optional[
                                    DataType] = DataType.UNDEFINED,
                                access_rights: Optional[
                                    AccessRights] = AccessRights.MANAGE):
        pass

    def write_service_bus_topic(self,
                                name: str,
                                connection: str,
                                topic_name: str,
                                subscription_name: str,
                                data_type: Optional[
                                    DataType] = DataType.UNDEFINED,
                                access_rights: Optional[
                                    AccessRights] = AccessRights.MANAGE):
        pass

    def on_queue_change(self,
                        name: str,
                        queue_name: str,
                        connection: str,
                        data_type: Optional[DataType] = DataType.UNDEFINED):
        pass

    def write_queue(self,
                    name: str,
                    queue_name: str,
                    connection: str,
                    data_type: Optional[DataType] = DataType.UNDEFINED):
        pass

    def on_event_hub_message(self,
                             name: str,
                             connection: str,
                             event_hub_name: str,
                             data_type: Optional[DataType] = DataType.UNDEFINED,
                             cardinality: Optional[
                                 Cardinality] = Cardinality.MANY,
                             consumer_group: Optional[str] = "$Default"):
        pass

    def write_event_hub_message(self,
                                name: str,
                                connection: str,
                                event_hub_name: str,
                                data_type: Optional[DataType] =
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
                            create_lease_collection_if_not_exists: Optional[
                                bool] = False,
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
        pass

    def write_cosmos_db_documents(self,
                                  name: str,
                                  database_name: str,
                                  collection_name: str,
                                  connection_string_setting: str,
                                  create_if_not_exists: Optional[bool] = False,
                                  partition_key: Optional[str] = None,
                                  collection_throughput: Optional[int] = -1,
                                  use_multiple_write_locations: Optional[
                                      bool] = False,
                                  preferred_locations: Optional[str] = None,
                                  data_type: Optional[
                                      DataType] = DataType.UNDEFINED):
        pass

    def read_cosmos_db_documents(self,
                                 name: str,
                                 database_name: str,
                                 collection_name: str,
                                 connection_string_setting: str,
                                 document_id: Optional[str] = None,
                                 sql_query: Optional[str] = None,
                                 partition_key: Optional[str] = None,
                                 data_type: Optional[
                                     DataType] = DataType.UNDEFINED):
        pass
