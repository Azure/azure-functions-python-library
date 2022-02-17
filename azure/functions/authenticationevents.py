from importlib import import_module
import json
from logging import exception
import pickle
from re import I
from typing_extensions import Self
from xmlrpc.client import DateTime
from azure.functions import HttpRequest
from azure.functions import HttpResponse

import typing
import urllib
from enum import Enum, auto
import uuid

from . import meta

#Utilities
def _serialize_custom_object(obj):
    """Serialize a user-defined object to JSON.

    This function gets called when `json.dumps` cannot serialize
    an object and returns a serializable dictionary containing enough
    metadata to recontrust the original object.

    Parameters
    ----------
    obj: Object
        The object to serialize

    Returns
    -------
    dict_obj: A serializable dictionary with enough metadata to reconstruct
              `obj`

    Exceptions
    ----------
    TypeError:
        Raise if `obj` does not contain a `to_json` attribute
    """
    # 'safety' guard: raise error if object does not
    # support serialization
    if not hasattr(obj, "to_json"):
        raise TypeError(f"class {type(obj)} does not expose a `to_json` "
                        "function")
    # Encode to json using the object's `to_json`
    obj_type = type(obj)
    return {
        "__class__": obj.__class__.__name__,
        "__module__": obj.__module__,
        "__data__": obj_type.to_json(obj)
    }


def _deserialize_custom_object(obj: dict) -> object:
    """Deserialize a user-defined object from JSON.

    Deserializes a dictionary encoding a custom object,
    if it contains class metadata suggesting that it should be
    decoded further.

    Parameters:
    ----------
    obj: dict
        Dictionary object that potentially encodes a custom class

    Returns:
    --------
    object
        Either the original `obj` dictionary or the custom object it encoded

    Exceptions
    ----------
    TypeError
        If the decoded object does not contain a `from_json` function

        testing
    """
    if ("__class__" in obj) and ("__module__" in obj) and ("__data__" in obj):
        class_name = obj.pop("__class__")
        module_name = obj.pop("__module__")
        obj_data = obj.pop("__data__")

        # Importing the class
        module = import_module(module_name)
        class_ = getattr(module, class_name)

        if not hasattr(class_, "from_json"):
            raise TypeError(f"class {type(obj)} does not expose a `from_json` "
                            "function")

        # Initialize the object using its `from_json` deserializer
        obj = class_.from_json(obj_data)
    return obj

class RequestStatus(Enum):
     Failed = auto()
     TokenInvalid = auto()
     Successful = auto()

class IEventResponse():
    def __init__(self, HttpResponseMessage: HttpResponse,
                 Schema : str,
                 Body: str,
                 JsonBody):
                 self.HttpResponseMessage=HttpResponseMessage
                 self.Schema= Schema
                 self.Body=Body
                 self.JsonBody=JsonBody

    
    def get_Body(self):
        return self.HttpResponseMessage.get_body        

    def set_Body(self,value):
        if self.HttpResponseMessage is None:
            self.HttpResponseMessage = HttpResponse()
            self.HttpResponseMessage.__set_body(value)

    def invalidate():
        pass


    def get_JsonBody(self):
        return json.dump(self.Body)

    def set_JsonBody(self, value):
        self.Body = str(value)

    def set_JsonValue(self, paths, value):
        payload = json.dumps(self.Body)
        current = payload
        last=""
        for path in paths:
            current=current[path]
            last=path
            if current is None:
                pass #Throw exception
        
        current[path] = value
        body = str(payload)
    
    @staticmethod
    def CreateInstance(type : type, schema : str, body : str):
        response =IEventResponse(type())
        response.Schema = schema
        response.Body = body
        return response

class IEventData():
    def __init__(self):
        pass
    @classmethod
    def GetCustomJsonConverters():
        return
    @classmethod
    def FromJson(json:str) :
        jsonString = json.loads(json)
        return IEventData(**jsonString)

    @staticmethod
    def CreateInstance(Type,json:str):
        data = IEventData(Type())
        return data if not json else data.FromJson(json)


class IEventRequest():
    def __init__(self,
                HttpRequestMessage: HttpRequest,
                StatusMessage: str,
                RequestStatus: RequestStatus,
                response: IEventResponse,
                payload: IEventData,
                name: str):
        self._HttpRequestMessage=HttpRequestMessage
        self._StatusMessage=StatusMessage
        self._RequestStatus=RequestStatus
        self.response=response
        self.payload=payload
        self.name=name

    def ToString(self):
        return pickle.dumps(self)
    
    def InstanceCreated(args):
        pass

    def Failed(message: str):
        response=HttpResponse()
        response.status_code=400
        response.__set_body(message)
        return response

    def Completed(self, response: IEventResponse):
        try:
            if self._RequestStatus == RequestStatus.TokenInvalid:
                return HttpResponse(status_code=401)
            if self._RequestStatus == RequestStatus.Failed:
              return self.Failed()
            # response.Validate()
            return HttpResponse(status_code=200,body=response.JsonBody)
        except exception as ex:
            return self.Failed(ex.msg)

class TokenIssuanceStartResponse(IEventResponse):
    def __init__(self,
                Description: str):
                self.Description=Description
    
    def get_Description(self):
        return self.Description
    
    def set_Description(self,value):
        self.Description=value

    def invalidate(self):
        self.set_JsonValue(["addition","description"], self.Description)

class AuthProtocol():
    def __init__(self,
                Type: str,
                TenantId: uuid):
                self.Type=Type
                self.TenantId=TenantId
class Client():
    def __init__(self,
                Ip: str):
                self.Ip=Ip


class Role():
    def __init__(self,
                Id: uuid,
                Value: str):
                self.Id=Id
                self.Value=Value

class ServicePrincipalName():
    def __init__(self,
                Url: str,
                Uuid: uuid):
                self.Url=Url
                self.Uuid=Uuid

listOfServicePrincipalName= list[ServicePrincipalName]

class ServicePrincipal():
    def __init__(self,
                Id: uuid,
                AppId: uuid,
                AppDisplayName: str,
                DisplayName: str,
                ServicePrincipalNames: listOfServicePrincipalName):
                self.Id=Id
                self.AppId=AppId
                self.AppDisplayName=AppDisplayName
                self.DisplayName=DisplayName
                self.ServicePrincipalNames=ServicePrincipalNames

class User():
    def __init__(self,
                AgeGroup:str,
                CompanyName:str,
                Country:str,
                CreatedDateTime:DateTime,
                CreationType:str,
                Department:str,
                DisplayName:str,
                GivenName:str,
                LastPasswordChangeDateTime:DateTime,
                Mail:str,
                OnPremisesSamAccountName:str,
                OnPremisesSecurityIdentifier:str,
                OnPremiseUserPrincipalName:str,
                PreferredDataLocation:str,
                PreferredLanguage:str,
                Surname:str,
                UserPrincipalName:str,
                UserType:str):
                self.UserType=UserType
                self.UserPrincipalName=UserPrincipalName
                self.Surname=Surname
                self.PreferredLanguage=PreferredLanguage
                self.AgeGroup=AgeGroup
                self.CompanyName=CompanyName
                self.Country=Country
                self.CreatedDateTime=CreatedDateTime
                self.CreationType=CreationType
                self.Department=Department
                self.DisplayName=DisplayName
                self.GivenName=GivenName
                self.LastPasswordChangeDateTime=LastPasswordChangeDateTime
                self.Mail=Mail
                self.OnPremisesSamAccountName=OnPremisesSamAccountName
                self.OnPremisesSecurityIdentifier=OnPremisesSecurityIdentifier
                self.OnPremiseUserPrincipalName=OnPremiseUserPrincipalName
                self.PreferredDataLocation=PreferredDataLocation

Roles=list[Role]

class Context():
    def __init__(self,
                CorrelationId:uuid,
                Client:Client,
                AuthProtocol:AuthProtocol,
                ClientServicePrincipal: ServicePrincipal,
                ResourceServicePrincipal: ServicePrincipal,
                Roles: Roles,
                User: User):
                self.User=User
                self.Roles=Roles
                self.ResourceServicePrincipal=ResourceServicePrincipal
                self.ClientServicePrincipal=ClientServicePrincipal
                self.AuthProtocol=AuthProtocol
                self.Client=Client
                self.CorrelationId=CorrelationId

class TokenIssuanceStartData(IEventData):
    def __init__(self,
                EventId: uuid,
                EventTime: DateTime,
                EventVersion: str,
                EventType: str,
                Context: str):
                self.Context=Context
                self.EventType=EventType
                self.EventVersion=EventVersion
                self.EventTime=EventTime
                self.EventId=EventId



class TokenIssuanceStartRequest(IEventRequest):
    def __init__(self,
                response: TokenIssuanceStartResponse,
                payload: TokenIssuanceStartData,
                TokenClaims: dict[str,str]):
                self.TokenClaims=TokenClaims
                self.response=response
                self.payload=payload

    def InstanceCreated(self,args: list):
        self.TokenClaims=args[0]
        
                

        
# Authentication Event Trigger
class AuthenticationEventTriggerConverter(meta.InConverter,
                               meta.OutConverter,
                               binding='authenticationEventTrigger',
                               trigger=True):
    @classmethod
    def check_input_type_annotation(cls, pytype):
        # Activity Trigger's arguments should accept any types
        return True

    @classmethod
    def check_output_type_annotation(cls, pytype):
        # The activity trigger should accept any JSON serializable types
        return True

    @classmethod
    def decode(cls,
               data: meta.Datum, *,
               trigger_metadata) -> typing.Any:
        data_type = data.type

        # Durable functions extension always returns a string of json
        # See durable functions library's call_activity_task docs
        if data_type in ['string', 'json']:
            try:
                callback = _deserialize_custom_object
                result = json.loads(data.value, object_hook=callback)
            except json.JSONDecodeError:
                # String failover if the content is not json serializable
                result = data.value
            except Exception:
                raise ValueError(
                    'authentication event trigger input must be a string or a '
                    f'valid json serializable ({data.value})')
        else:
            raise NotImplementedError(
                f'unsupported authentication event trigger payload type: {data_type}')

        return result

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type]) -> meta.Datum:
        try:
            callback = _serialize_custom_object
            result = json.dumps(obj, default=callback)
        except TypeError:
            raise ValueError(
                f'authentication event trigger output must be json serializable ({obj})')

        return meta.Datum(type='json', value=result)

    @classmethod
    def has_implicit_output(cls) -> bool:
        return True


