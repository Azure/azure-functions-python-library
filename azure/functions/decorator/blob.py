from azure.functions.decorator._abc import InputBinding, DataType, \
    OutputBinding, Trigger


class BlobOutput(OutputBinding):
    @staticmethod
    def get_binding_name():
        return "blob"

    def __init__(self, name: str, connection: str, path: str,
                 data_type: DataType):
        self.connection: str = connection
        self.path: str = path
        self.data_type: str = data_type.name.lower()
        super().__init__(name=name)

    def get_dict_repr(self):
        return {
            "type": self.get_binding_name(),
            "direction": self.get_binding_direction(),
            "name": self.name,
            "dataType": self.data_type,
            "path": self.path,
            "connection": self.connection
        }


class BlobInput(InputBinding):
    @staticmethod
    def get_binding_name():
        return "blob"

    def __init__(self, name: str, connection: str,
                 path: str, data_type: DataType):
        self.connection: str = connection
        self.path: str = path
        self.data_type: str = data_type.name.lower()
        super().__init__(name=name)

    def get_dict_repr(self):
        return {
            "type": self.get_binding_name(),
            "direction": self.get_binding_direction(),
            "name": self.name,
            "dataType": self.data_type,
            "path": self.path,
            "connection": self.connection
        }


class BlobTrigger(Trigger):

    @staticmethod
    def get_binding_name():
        return "blobTrigger"

    def __init__(self, name: str, connection: str, path: str, data_type: str):
        self.connection = connection
        self.path = path
        self.data_type = data_type
        super().__init__(name=name)

    def get_dict_repr(self):
        return {
            "type": self.get_binding_name(),
            "direction": self.get_binding_direction(),
            "name": self.name,
            "dataType": self.data_type,
            "path": self.path,
            "connection": self.connection
        }