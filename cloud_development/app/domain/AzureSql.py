import datetime
from decimal import Decimal

class AzureSql():
    def __init__(self,id:str,subscriptionId:str,resourceGroup:str,sqlServer:str,
                 kind:str,name:str):
        self.id = id
        self.subscriptionId = subscriptionId
        self.resourceGroup = resourceGroup
        self.sqlServer = sqlServer
        self.kind = kind
        self.name = name