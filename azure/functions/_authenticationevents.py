from abc import ABC, abstractmethod
import json
import azure.functions._abc as _abc
from xmlrpc.client import DateTime
import uuid



class ITokenIssuanceAction(_abc.IAuthenticationEventAction):
    def __init__(self,
                actionType):
                self.actionType=actionType
    
    abstractmethod
    def build_action_body():
        pass

class Claim():
    def __init__(self,
                id: str,
                values: list[str]):
                self.id=id
                self.values=values

class ProvideClaimsForToken(ITokenIssuanceAction):
    def __init__(self,
                claims: list[Claim]):
                self.actionType="ProvideClaimsForToken"
                self.claims=claims

    def add_claim(self,id: str, values: list[str]):
        self.claims.append(Claim(Id=id,Values=values))

    def build_action_body(self):
        temp:dict
        for item in self.claims:
            temp[item.Id]=item.Values
        return json.dumps(temp)

class IActionableResponse(_abc.IAuthenticationEventResponse,_abc.IAuthenticationEventActionable):
    def __init__(self,
                actions: list[_abc.IAuthenticationEventAction]):
                self.actions=actions

    def invalidate_actions(self):
        actionElement = "actions"
        typeProperty = "type"
        Payload = self.JsonBody
        

    def invalidate(self):
        self.invalidate_actions()

class AuthProtocol():
    def __init__(self,
                type: str,
                tenantId: str):
                self.type=type
                self.tenantId=tenantId

    def populate(authProtocol: dict):
        return AuthProtocol(**authProtocol)
class Client():
    def __init__(self,
                ip: str):
                self.ip=ip
    def populate(client: dict):
        return Client(**client)


class Role():
    def __init__(self,
                id: str,
                value: str):
                self.id=id
                self.value=value

class ServicePrincipalName():
    def __init__(self,
                url: str,
                uuid: uuid):
                self.url=url
                self.uuid=uuid

listOfServicePrincipalName= list[ServicePrincipalName]

class ServicePrincipal():
    def __init__(self,
                id: str,
                appId: str,
                appDisplayName: str,
                displayName: str,
                servicePrincipalNames: list[str]):
                self.id=id
                self.appId=appId
                self.appDisplayName=appDisplayName
                self.displayName=displayName
                self.servicePrincipalNames=servicePrincipalNames
    def populate(servicePrincipal: dict):
        return ServicePrincipal(**servicePrincipal)

class User():
    def __init__(self,
                ageGroup:str,
                companyName:str,
                country:str,
                createdDateTime:str,
                creationType:str,
                department:str,
                displayName:str,
                givenName:str,
                lastPasswordChangeDateTime:str,
                mail:str,
                onPremisesSamAccountName:str,
                onPremisesSecurityIdentifier:str,
                onPremiseUserPrincipalName:str,
                preferredDataLocation:str,
                preferredLanguage:str,
                surname:str,
                userPrincipalName:str,
                userType:str,
                id:str):
                self.id=id
                self.userType=userType
                self.userPrincipalName=userPrincipalName
                self.surname=surname
                self.preferredLanguage=preferredLanguage
                self.ageGroup=ageGroup
                self.companyName=companyName
                self.country=country
                self.createdDateTime=createdDateTime
                self.creationType=creationType
                self.department=department
                self.displayName=displayName
                self.givenName=givenName
                self.lastPasswordChangeDateTime=lastPasswordChangeDateTime
                self.mail=mail
                self.onPremisesSamAccountName=onPremisesSamAccountName
                self.onPremisesSecurityIdentifier=onPremisesSecurityIdentifier
                self.onPremiseUserPrincipalName=onPremiseUserPrincipalName
                self.preferredDataLocation=preferredDataLocation

    def populate(user: dict):
        return User(**user)

                

Roles=list[Role]


class Context():
    def __init__(self,
                correlationId:str,
                client:Client,
                authProtocol:AuthProtocol,
                clientServicePrincipal: ServicePrincipal,
                resourceServicePrincipal: ServicePrincipal,
                roles: Roles,
                user: User):
                self.user=user
                self.roles=roles
                self.resourceServicePrincipal=resourceServicePrincipal
                self.clientServicePrincipal=clientServicePrincipal
                self.authProtocol=authProtocol
                self.client=client
                self.correlationId=correlationId
    
    def populate(context: dict):
        return Context(correlationId=context.get('correlationId'),
        user=User.populate(context.get('user')),
        client=Client.populate(context.get('client')),
        clientServicePrincipal=ServicePrincipal.populate(context.get('clientServicePrincipal')),
        resourceServicePrincipal=ServicePrincipal.populate(context.get('resourceServicePrincipal')),
        roles=context.get('roles'),
        authProtocol=AuthProtocol.populate(context.get('authProtocol')))

class preview_10_01_2021():
    class TokenIssuanceStartResponse(_abc.IAuthenticationEventResponse):
        def __init__(self):
            pass
                    # super().__init__(kargs)
                    

    class TokenIssuanceStartData(_abc.IAuthenticationEventData):
        def __init__(self,
                    eventListenerId: str,
                    time: DateTime,
                    apiSchemaVersion: str,
                    type: str,
                    context: Context,
                    customExtensionId: str):
                    self.context=context
                    super.__init__(eventListenerId=eventListenerId, time=time,type=type,apiSchemaVersion=apiSchemaVersion,customExtensionId=customExtensionId)

        def create_instance(payload: dict):
            return preview_10_01_2021.TokenIssuanceStartData(eventListenerId=payload.get('eventListenerId'),time=payload.get('time'),type=payload.get('type'),apiSchemaVersion=payload.get('apiSchemaVersion'),context=Context.populate(payload.get('context')),customExtensionId=payload.get('customExtensionId'))


    class TokenIssuanceStartRequest(_abc.IAuthenticationEventRequest):
        def __init__(self,
                    response: _abc.IAuthenticationEventResponse,
                    payload: _abc.IAuthenticationEventData,
                    tokenClaims: dict[str,str]):
                    self.tokenClaims=tokenClaims
                    self.response=response
                    self.payload=payload

        def create_instance(result:dict):
            response=preview_10_01_2021.TokenIssuanceStartResponse()
            data=preview_10_01_2021.TokenIssuanceStartData.create_instance(payload=result.get('payload'))
            tokenclaims=result.get('tokenClaims') 
            return preview_10_01_2021.TokenIssuanceStartRequest(payload=data,response=response,tokenClaims=tokenclaims)
            